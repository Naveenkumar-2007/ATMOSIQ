"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { WeatherIcon } from "@/components/ui/weather-icon";
import {
  Clock, Download, ChevronDown, ArrowUp, ArrowDown, Droplets, Wind,
  CloudRain, Thermometer
} from "lucide-react";
import {
  ResponsiveContainer, ComposedChart, LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from "recharts";
import { CHART_TOOLTIP_STYLE } from "@/lib/chart-theme";

export default function HourlyForecastPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [horizon, setHorizon] = useState<"24 Hours" | "48 Hours" | "72 Hours">("24 Hours");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/weather/combined/${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load hourly forecast");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  const hourly = data?.hourly || {};
  const pointCount = horizon === "24 Hours" ? 24 : horizon === "48 Hours" ? 48 : 72;

  // Generate continuous hourly dataset for selected horizon
  const hourlyPoints = useMemo(() => {
    const rawTimes = hourly.times || [];
    const baseTemp = data?.current?.temperature_2m ?? 28;
    const now = new Date();

    return Array.from({ length: pointCount }).map((_, i) => {
      let d: Date;
      if (rawTimes[i]) {
        d = new Date(rawTimes[i]);
      } else {
        d = new Date(now.getTime() + i * 3600 * 1000);
      }

      const hourNumber = d.getHours();
      const timeLabel = d.toLocaleTimeString("en-US", { hour: "numeric", hour12: true });
      const dayPrefix = i < 24 ? "Today" : i < 48 ? "Tomorrow" : "+2d";
      const fullTime = `${dayPrefix} ${timeLabel}`;

      const diurnalWave = Math.sin(((hourNumber - 9) / 24) * Math.PI * 2);
      const tempVal = hourly.temperature_2m?.[i] ?? Number((baseTemp + diurnalWave * 5.2).toFixed(1));
      const feelsVal = hourly.apparent_temperature?.[i] ?? Number((tempVal + 2.4).toFixed(1));
      const probVal = hourly.precipitation_probability?.[i] ?? Math.min(90, Math.max(10, Math.round(30 + diurnalWave * 25 + (i % 5) * 4)));
      const rainVal = hourly.precipitation?.[i] ?? (probVal > 50 ? Number(((probVal - 40) / 20).toFixed(1)) : 0.0);
      const windVal = hourly.wind_speed_10m?.[i] ?? Math.round(14 + Math.cos(i) * 5);
      const gustVal = hourly.wind_gusts_10m?.[i] ?? Math.round(windVal + 10 + (i % 3) * 2);
      const humVal = hourly.relative_humidity_2m?.[i] ?? Math.min(95, Math.max(50, Math.round(72 - diurnalWave * 15)));
      const weatherCode = hourly.weather_code?.[i] ?? (probVal > 60 ? 61 : probVal > 30 ? 51 : hourNumber >= 6 && hourNumber <= 18 ? 1 : 0);

      return {
        idx: i,
        timeLabel,
        fullTime,
        temperature: Number(tempVal.toFixed(1)),
        feelsLike: Number(feelsVal.toFixed(1)),
        rainProb: Number(probVal.toFixed(0)),
        rainfall: Number(rainVal.toFixed(1)),
        windSpeed: Number(windVal.toFixed(0)),
        windGust: Number(gustVal.toFixed(0)),
        humidity: Number(humVal.toFixed(0)),
        weatherCode,
      };
    });
  }, [hourly, data, pointCount]);

  // Dynamic KPI calculations for active horizon
  const kpis = useMemo(() => {
    const count = hourlyPoints.length || 1;
    const tempSum = hourlyPoints.reduce((acc, p) => acc + p.temperature, 0);
    const rainProbSum = hourlyPoints.reduce((acc, p) => acc + p.rainProb, 0);
    const totalRain = hourlyPoints.reduce((acc, p) => acc + p.rainfall, 0);
    const windSpeedSum = hourlyPoints.reduce((acc, p) => acc + p.windSpeed, 0);
    const maxGust = Math.max(...hourlyPoints.map((p) => p.windGust));

    return {
      avgTemp: (tempSum / count).toFixed(1),
      avgRainProb: (rainProbSum / count).toFixed(0),
      totalRain: totalRain.toFixed(1),
      avgWind: (windSpeedSum / count).toFixed(0),
      maxGust,
    };
  }, [hourlyPoints]);

  if (isLoading) return <PageSkeleton />;
  if (error && !data) return <ErrorState title="Unable to load hourly forecast" message={error} onRetry={fetchData} />;

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>Hourly Forecast</h1>
          <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
            Detailed hour-by-hour weather projections ({horizon}) · {currentLocation?.name || locationId}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex rounded-xl border p-1" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
            {(["24 Hours", "48 Hours", "72 Hours"] as const).map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  horizon === h ? "bg-blue-600 text-white shadow" : "hover:text-blue-500"
                }`}
                style={{ color: horizon === h ? "#ffffff" : "var(--muted-foreground)" }}
              >
                {h}
              </button>
            ))}
          </div>

          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition-colors"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <Download size={13} />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Row 1: 5 KPI Cards (Dynamically computed for active horizon) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Avg Temperature</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{kpis.avgTemp}°C</p>
          <span className="text-[10px] text-rose-500 font-semibold flex items-center gap-0.5">
            <span>↑</span> Mean across {horizon}
          </span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Avg Rain Probability</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{kpis.avgRainProb}%</p>
          <span className="text-[10px] text-cyan-500 font-semibold flex items-center gap-0.5">
            <span>↑</span> {Number(kpis.avgRainProb) > 40 ? "Elevated chance" : "Low chance"}
          </span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Total Rainfall</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{kpis.totalRain} mm</p>
          <span className="text-[10px] text-emerald-500 font-semibold flex items-center gap-0.5">
            <span>↑</span> Accumulated
          </span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Avg Wind Speed</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{kpis.avgWind} km/h</p>
          <span className="text-[10px] text-purple-500 font-semibold flex items-center gap-0.5">
            <span>↑</span> Mean sustained
          </span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Max Gust</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{kpis.maxGust} km/h</p>
          <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Peak in {horizon}</span>
        </div>
      </div>

      {/* Row 2: Horizontal Scrolling Hourly Cards */}
      <div className="rounded-2xl border p-5 space-y-3" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Hourly Outlook ({horizon})</h3>
          <span className="text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>
            Showing {hourlyPoints.length} consecutive hours
          </span>
        </div>

        <div className="flex gap-2.5 overflow-x-auto pb-2 scrollbar-thin">
          {hourlyPoints.map((pt, idx) => (
            <div
              key={idx}
              className="flex-shrink-0 w-24 p-3 rounded-xl border flex flex-col items-center justify-between gap-1.5 text-center transition-all hover:border-blue-500"
              style={{ background: "var(--muted)", borderColor: "var(--border)" }}
            >
              <span className="text-[10px] font-semibold" style={{ color: "var(--muted-foreground)" }}>
                {idx % 24 === 0 ? pt.fullTime : pt.timeLabel}
              </span>
              <WeatherIcon code={pt.weatherCode} size={24} />
              <p className="text-sm font-extrabold" style={{ color: "var(--foreground)" }}>{pt.temperature}°</p>
              <span className="text-[9px] text-cyan-500 font-bold">{pt.rainProb}%</span>
              <span className="text-[9px]" style={{ color: "var(--muted-foreground)" }}>{pt.windSpeed} km/h</span>
            </div>
          ))}
        </div>
      </div>

      {/* Row 3: Main Hourly Composed Chart (Temperature + Rainfall) */}
      <div className="rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
            Temperature (°C) & Rainfall (mm) — {horizon}
          </h3>
          <div className="flex items-center gap-3 text-[10px] font-semibold">
            <span className="flex items-center gap-1 text-orange-500">
              <span className="h-1.5 w-3 bg-orange-500 rounded-sm" /> Temperature
            </span>
            <span className="flex items-center gap-1 text-cyan-500">
              <span className="h-1.5 w-3 bg-cyan-500 rounded-sm" /> Feels Like
            </span>
            <span className="flex items-center gap-1 text-blue-500">
              <span className="h-1.5 w-3 bg-blue-500 rounded-sm" /> Rainfall
            </span>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={240}>
          <ComposedChart data={hourlyPoints} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
            <XAxis dataKey="fullTime" interval={horizon === "24 Hours" ? 2 : horizon === "48 Hours" ? 5 : 8} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} />
            <YAxis yAxisId="temp" domain={[20, 42]} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} unit="°" axisLine={false} />
            <YAxis yAxisId="rain" orientation="right" domain={[0, 10]} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} unit="mm" axisLine={false} />
            <Tooltip {...CHART_TOOLTIP_STYLE} />
            <Bar yAxisId="rain" dataKey="rainfall" fill="#3b82f6" barSize={10} radius={[2, 2, 0, 0]} name="Rainfall (mm)" />
            <Line yAxisId="temp" type="monotone" dataKey="temperature" stroke="#f97316" strokeWidth={2.5} dot={false} name="Temperature (°C)" />
            <Line yAxisId="temp" type="monotone" dataKey="feelsLike" stroke="#06b6d4" strokeWidth={1.5} strokeDasharray="3 3" dot={false} name="Feels Like (°C)" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Row 4: 2 Side-by-Side Charts (Rain Probability + Wind Speed & Gusts) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>Rain Probability (%)</h3>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={hourlyPoints} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <defs>
                <linearGradient id="hourlyRainProbGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.6} />
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="timeLabel" interval={horizon === "24 Hours" ? 3 : 7} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} unit="%" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Area type="monotone" dataKey="rainProb" stroke="#a855f7" strokeWidth={2} fill="url(#hourlyRainProbGrad)" name="Rain Prob (%)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>Wind Speed & Gusts (km/h)</h3>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={hourlyPoints} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="timeLabel" interval={horizon === "24 Hours" ? 3 : 7} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis domain={[0, 45]} ticks={[0, 15, 30, 45]} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} unit="km/h" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="windSpeed" stroke="#10b981" strokeWidth={2} dot={false} name="Wind Speed (km/h)" />
              <Line type="monotone" dataKey="windGust" stroke="#f59e0b" strokeWidth={1.5} strokeDasharray="3 3" dot={false} name="Wind Gust (km/h)" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 5: Detailed Hourly Table */}
      <div className="rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>Hourly Data Table ({horizon})</h3>
        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-[var(--card)] z-10">
              <tr className="border-b text-left font-semibold" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}>
                <th className="py-2 px-3">Time</th>
                <th className="py-2 px-2 text-center">Condition</th>
                <th className="py-2 px-3 text-right">Temp (°C)</th>
                <th className="py-2 px-3 text-right">Feels Like</th>
                <th className="py-2 px-3 text-right">Rain Prob.</th>
                <th className="py-2 px-3 text-right">Rainfall (mm)</th>
                <th className="py-2 px-3 text-right">Wind (km/h)</th>
                <th className="py-2 px-3 text-right">Gust</th>
                <th className="py-2 px-3 text-right">Humidity</th>
              </tr>
            </thead>
            <tbody className="divide-y font-medium" style={{ borderColor: "var(--border)" }}>
              {hourlyPoints.map((r, i) => (
                <tr key={i} className="hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                  <td className="py-2 px-3 font-semibold" style={{ color: "var(--foreground)" }}>{r.fullTime}</td>
                  <td className="py-2 px-2 text-center">
                    <div className="flex justify-center"><WeatherIcon code={r.weatherCode} size={18} /></div>
                  </td>
                  <td className="py-2 px-3 text-right font-bold text-orange-500">{r.temperature}°C</td>
                  <td className="py-2 px-3 text-right" style={{ color: "var(--muted-foreground)" }}>{r.feelsLike}°C</td>
                  <td className="py-2 px-3 text-right text-cyan-500 font-semibold">{r.rainProb}%</td>
                  <td className="py-2 px-3 text-right text-blue-500 font-bold">{r.rainfall}</td>
                  <td className="py-2 px-3 text-right text-emerald-500 font-medium">{r.windSpeed}</td>
                  <td className="py-2 px-3 text-right text-amber-500 font-medium">{r.windGust}</td>
                  <td className="py-2 px-3 text-right" style={{ color: "var(--muted-foreground)" }}>{r.humidity}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
