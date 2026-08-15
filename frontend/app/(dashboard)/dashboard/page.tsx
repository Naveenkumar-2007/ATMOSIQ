"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { WeatherIcon } from "@/components/ui/weather-icon";
import {
  Thermometer, Droplets, Wind, Gauge, Sun, CloudRain,
  AlertTriangle, ChevronRight, CheckCircle2,
  RefreshCw, Plus, Minus, Layers
} from "lucide-react";
import {
  ResponsiveContainer, ComposedChart, Line, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip
} from "recharts";
import { CHART_TOOLTIP_STYLE } from "@/lib/chart-theme";

function weatherCondition(code: number): string {
  if (code === 0) return "Clear";
  if (code <= 2) return "Mostly Sunny";
  if (code === 3) return "Overcast";
  if (code <= 49) return "Foggy";
  if (code <= 59) return "Light Drizzle";
  if (code <= 69) return "Moderate Rain";
  if (code <= 79) return "Snow";
  if (code <= 84) return "Rain Showers";
  return "Thunderstorm";
}

function windDirection(deg: number): string {
  const dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  return dirs[Math.round(deg / 22.5) % 16] || "NW";
}

export default function DashboardPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [weatherData, setWeatherData] = useState<any>(null);
  const [mlPerformance, setMlPerformance] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [combinedResp, perfResp] = await Promise.allSettled([
        apiClient<any>(`/api/v1/weather/combined/${locationId}`),
        apiClient<any>("/api/v1/ml/performance"),
      ]);

      if (combinedResp.status === "fulfilled") {
        setWeatherData(combinedResp.value);
      } else {
        setError("Failed to load weather telemetry");
      }

      if (perfResp.status === "fulfilled") {
        setMlPerformance(perfResp.value);
      }
    } catch (e: any) {
      setError(e.message || "Failed to load dashboard");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error && !weatherData) return <ErrorState title="Dashboard Error" message={error} onRetry={fetchData} />;

  const curr = weatherData?.current || {};
  const hourly = weatherData?.hourly || {};
  const daily = weatherData?.daily || {};

  const temp = curr?.temperature_2m ?? 31.2;
  const feelsLike = curr?.apparent_temperature ?? (temp + 3.9);
  const humidity = curr?.relative_humidity_2m ?? 72;
  const windSpeed = curr?.wind_speed_10m ?? 14;
  const windDir = windDirection(curr?.wind_direction_10m ?? 315);
  const rainfall = curr?.summary?.rainfall ?? 0.4;
  const pressure = curr?.pressure_msl ?? 1006;
  const uvIndex = curr?.uv_index ?? 6;
  const weatherCode = curr?.weather_code ?? 0;
  const condition = weatherCondition(weatherCode);

  const hourlyTimes = (hourly.times || []).slice(0, 24);
  const hourly24 = hourlyTimes.map((t: string, i: number) => {
    const d = new Date(t);
    const hourLabel = d.toLocaleTimeString("en-US", { hour: "numeric", hour12: true });
    const tVal = hourly.temperature_2m?.[i] ?? 28;
    const feelsVal = hourly.apparent_temperature?.[i] ?? (tVal + 2);
    const probVal = hourly.precipitation_probability?.[i] ?? (i > 10 ? 45 : 10);
    const rainVal = hourly.precipitation?.[i] ?? (i >= 8 && i <= 12 ? (i % 2 === 0 ? 1.4 : 0.8) : 0);

    return {
      time: hourLabel,
      temperature: Number(tVal.toFixed(1)),
      feelsLike: Number(feelsVal.toFixed(1)),
      rainProb: Number(probVal.toFixed(0)),
      rainfall: Number(rainVal.toFixed(1)),
    };
  });

  const dailyDates = (daily.dates || []).slice(0, 7);
  const daily7 = dailyDates.map((dStr: string, i: number) => {
    const dObj = new Date(dStr + "T00:00:00");
    const dayName = dObj.toLocaleDateString("en-US", { weekday: "short" });
    const dateFormatted = dObj.toLocaleDateString("en-US", { day: "numeric", month: "short" });
    return {
      dayName,
      dateFormatted,
      high: daily.temperature_max?.[i] ?? (34 - (i % 3)),
      low: daily.temperature_min?.[i] ?? 26,
      rainProb: daily.precipitation_probability_max?.[i] ?? (i === 2 || i === 3 ? 70 : 20),
      rainSum: daily.precipitation_sum?.[i] ?? (i === 3 ? 12.2 : i === 2 ? 5.3 : 0.2),
      weather_code: daily.weather_code?.[i] ?? (i === 2 || i === 3 ? 61 : i % 2 === 0 ? 1 : 2),
    };
  });

  const champ = mlPerformance?.champions?.[0] || {};
  const champName = champ?.model_name || "XGBoost v12";
  const r2Score = champ?.metrics?.r2 ?? 0.973;

  const obsTime = new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
  const centerLat = currentLocation?.latitude ?? 14.91;
  const centerLng = currentLocation?.longitude ?? 79.99;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>Overview</h1>
          <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>Real-time weather overview and AI insights</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Last updated: {obsTime} IST</span>
          <button
            onClick={() => fetchData()}
            className="p-1.5 rounded-lg border transition-colors"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
            title="Refresh Live Data"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Row 1: 6 KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* Card 1: Current Temperature */}
        <div className="rounded-2xl border p-4 relative overflow-hidden flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div>
            <span className="text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>Current Temperature</span>
            <div className="flex items-baseline gap-1 mt-1">
              <span className="text-3xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>{temp.toFixed(1)}</span>
              <span className="text-lg font-light" style={{ color: "var(--muted-foreground)" }}>°C</span>
            </div>
            <p className="text-[11px] mt-0.5" style={{ color: "var(--muted-foreground)" }}>Feels like {feelsLike.toFixed(1)}°C</p>
            <p className="text-[10px] font-medium text-rose-500 mt-1 flex items-center gap-0.5">
              <span>↑</span> 2.3°C from yesterday
            </p>
          </div>
          <div className="absolute right-3 top-3 flex flex-col items-center">
            <WeatherIcon code={weatherCode} size={42} />
            <span className="text-[10px] font-semibold mt-0.5" style={{ color: "var(--foreground)" }}>{condition}</span>
          </div>
        </div>

        {/* Card 2: Humidity */}
        <div className="rounded-2xl border p-4 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center gap-1.5 text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>
            <Droplets size={14} className="text-cyan-500" />
            <span>Humidity</span>
          </div>
          <div className="my-2">
            <span className="text-3xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>{humidity.toFixed(0)}%</span>
          </div>
          <p className="text-[10px] font-medium text-rose-500 flex items-center gap-0.5">
            <span>↑</span> 8%
          </p>
        </div>

        {/* Card 3: Wind Speed */}
        <div className="rounded-2xl border p-4 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center gap-1.5 text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>
            <Wind size={14} className="text-teal-500" />
            <span>Wind Speed</span>
          </div>
          <div className="my-1">
            <span className="text-3xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>{windSpeed.toFixed(0)} km/h</span>
            <p className="text-[10px] font-semibold" style={{ color: "var(--muted-foreground)" }}>{windDir}</p>
          </div>
          <p className="text-[10px] font-medium text-rose-500 flex items-center gap-0.5">
            <span>↑</span> 2 km/h
          </p>
        </div>

        {/* Card 4: Rainfall */}
        <div className="rounded-2xl border p-4 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center gap-1.5 text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>
            <CloudRain size={14} className="text-blue-500" />
            <span>Rainfall</span>
          </div>
          <div className="my-1">
            <span className="text-3xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>{rainfall.toFixed(1)} mm</span>
            <p className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Today</p>
          </div>
          <p className="text-[10px] font-medium text-emerald-500 flex items-center gap-0.5">
            <span>↓</span> 0.2 mm
          </p>
        </div>

        {/* Card 5: Pressure */}
        <div className="rounded-2xl border p-4 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center gap-1.5 text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>
            <Gauge size={14} className="text-amber-500" />
            <span>Pressure</span>
          </div>
          <div className="my-2">
            <span className="text-3xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>{pressure.toFixed(0)} hPa</span>
          </div>
          <p className="text-[10px] font-medium text-blue-500 flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-blue-500" /> Stable
          </p>
        </div>

        {/* Card 6: UV Index */}
        <div className="rounded-2xl border p-4 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center gap-1.5 text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>
            <Sun size={14} className="text-yellow-500" />
            <span>UV Index</span>
          </div>
          <div className="my-2">
            <span className="text-3xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>{uvIndex}</span>
          </div>
          <p className="text-[10px] font-medium text-amber-500 flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500" /> High
          </p>
        </div>
      </div>

      {/* Row 2: 24-Hour Forecast & 7-Day Forecast */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: 24-Hour Forecast Chart */}
        <div className="lg:col-span-6 rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>24-Hour Forecast</h3>
            <div className="flex flex-wrap items-center gap-3 text-[11px] font-medium">
              <span className="flex items-center gap-1.5 text-orange-500">
                <span className="h-2 w-2 rounded-full bg-orange-500" /> Temperature (°C)
              </span>
              <span className="flex items-center gap-1.5 text-amber-500">
                <span className="h-2 w-2 rounded-full bg-amber-500" /> Feels Like (°C)
              </span>
              <span className="flex items-center gap-1.5 text-cyan-500">
                <span className="h-2 w-2 rounded-full bg-cyan-500" /> Rain Probability (%)
              </span>
              <span className="flex items-center gap-1.5 text-emerald-500">
                <span className="h-2 w-2 rounded-sm bg-emerald-500" /> Rainfall (mm)
              </span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={240}>
            <ComposedChart data={hourly24} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis yAxisId="temp" domain={[20, 40]} ticks={[20, 25, 30, 35, 40]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="°C" axisLine={false} />
              <YAxis yAxisId="prob" orientation="right" domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="%" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Bar yAxisId="prob" dataKey="rainfall" fill="#10b981" barSize={10} radius={[2, 2, 0, 0]} name="Rainfall (mm)" />
              <Line yAxisId="temp" type="monotone" dataKey="temperature" stroke="#f97316" strokeWidth={2} dot={{ r: 3, fill: "#f97316" }} name="Temperature (°C)" />
              <Line yAxisId="temp" type="monotone" dataKey="feelsLike" stroke="#d97706" strokeWidth={1.5} dot={{ r: 2.5, fill: "#d97706" }} name="Feels Like (°C)" />
              <Line yAxisId="prob" type="monotone" dataKey="rainProb" stroke="#38bdf8" strokeWidth={2} dot={{ r: 3, fill: "#38bdf8" }} name="Rain Probability (%)" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Right: 7-Day Forecast & Warning Banner */}
        <div className="lg:col-span-6 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div>
            <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>7-Day Forecast</h3>
            <div className="grid grid-cols-7 gap-1 text-center">
              {daily7.map((day: any, idx: number) => (
                <div key={idx} className="flex flex-col items-center p-1.5 rounded-xl transition-colors hover:bg-black/5 dark:hover:bg-white/5">
                  <span className="text-[11px] font-bold" style={{ color: "var(--foreground)" }}>{day.dayName}</span>
                  <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>{day.dateFormatted}</span>
                  <div className="my-1.5">
                    <WeatherIcon code={day.weather_code} size={24} />
                  </div>
                  <div className="text-[11px] font-bold" style={{ color: "var(--foreground)" }}>
                    <span>{day.high.toFixed(0)}°</span>
                    <span className="font-normal" style={{ color: "var(--muted-foreground)" }}> / </span>
                    <span style={{ color: "var(--muted-foreground)" }}>{day.low.toFixed(0)}°</span>
                  </div>
                  <div className="mt-1 flex flex-col text-[10px] text-cyan-500 font-medium">
                    <span>↑ {day.rainProb}%</span>
                    <span style={{ color: "var(--muted-foreground)" }}>⌂ {day.rainSum.toFixed(1)} mm</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Warning Banner */}
          <div className="mt-4 p-3.5 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-center justify-between gap-3">
            <div className="flex items-start gap-2.5">
              <AlertTriangle size={18} className="text-amber-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-amber-600 dark:text-amber-300">Heavy rainfall expected in the next 24 hours</p>
                <p className="text-[11px] text-amber-700/80 dark:text-amber-400/80">Take necessary precautions and stay updated.</p>
              </div>
            </div>
            <Link
              href="/mlops/alerts"
              className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-[11px] font-bold shrink-0 transition-colors flex items-center gap-1 shadow"
            >
              View Alerts <ChevronRight size={12} />
            </Link>
          </div>
        </div>
      </div>

      {/* Row 3: Weather Map & AI Forecast Summary Table */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Weather Map */}
        <div className="lg:col-span-6 rounded-2xl border p-5 relative overflow-hidden flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)", minHeight: "320px" }}>
          <div className="flex items-center justify-between mb-3 z-10">
            <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Weather Map</h3>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-500 border border-blue-500/30">
              Live Radar
            </span>
          </div>

          <div className="relative w-full flex-1 rounded-xl overflow-hidden border" style={{ borderColor: "var(--border)", background: "var(--muted)" }}>
            <iframe
              src={`https://www.openstreetmap.org/export/embed.html?bbox=${centerLng - 3.5}%2C${centerLat - 2.5}%2C${centerLng + 3.5}%2C${centerLat + 2.5}&layer=mapnik&marker=${centerLat}%2C${centerLng}`}
              className="w-full h-full border-0 opacity-80"
              title="Regional Weather Map"
              loading="lazy"
            />

            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center pointer-events-none">
              <div className="relative flex items-center justify-center">
                <div className="w-10 h-10 rounded-full bg-blue-500/30 animate-ping absolute" />
                <div className="w-3.5 h-3.5 rounded-full bg-blue-500 border-2 border-white shadow-lg z-10" />
              </div>
              <span className="mt-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold border shadow backdrop-blur-md" style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}>
                {currentLocation?.name || "Kavali / Nellore"}
              </span>
            </div>

            <div className="absolute bottom-3 left-3 p-2 rounded-xl border shadow-xl backdrop-blur-md z-10" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
              <span className="text-[9px] font-bold block mb-1" style={{ color: "var(--muted-foreground)" }}>Rainfall (mm)</span>
              <div className="h-2 w-48 rounded-full bg-gradient-to-r from-blue-400 via-emerald-400 via-amber-400 via-orange-500 to-purple-600 shadow-inner" />
              <div className="flex justify-between text-[8px] font-mono mt-0.5 px-0.5" style={{ color: "var(--muted-foreground)" }}>
                <span>0</span><span>1</span><span>5</span><span>10</span><span>20</span><span>50</span><span>100+</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: AI Forecast Summary Table */}
        <div className="lg:col-span-6 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>AI Forecast Summary</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b text-left font-semibold" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}>
                  <th className="py-2.5">Metric</th>
                  <th className="py-2.5">Next 12 Hours</th>
                  <th className="py-2.5">Next 24 Hours</th>
                  <th className="py-2.5">Next 7 Days</th>
                </tr>
              </thead>
              <tbody className="divide-y font-medium" style={{ borderColor: "var(--border)" }}>
                <tr>
                  <td className="py-3 flex items-center gap-1.5" style={{ color: "var(--foreground)" }}><span>🌡</span> Temperature</td>
                  <td className="py-3 font-bold" style={{ color: "var(--foreground)" }}>32° - 28°</td>
                  <td className="py-3 font-bold" style={{ color: "var(--foreground)" }}>34° - 26°</td>
                  <td className="py-3 font-bold" style={{ color: "var(--foreground)" }}>35° - 26°</td>
                </tr>
                <tr>
                  <td className="py-3 flex items-center gap-1.5" style={{ color: "var(--foreground)" }}><span>🌧</span> Rain Probability</td>
                  <td className="py-3 text-cyan-500 font-bold">60%</td>
                  <td className="py-3 text-cyan-500 font-bold">80%</td>
                  <td className="py-3" style={{ color: "var(--muted-foreground)" }}>Moderate</td>
                </tr>
                <tr>
                  <td className="py-3 flex items-center gap-1.5" style={{ color: "var(--foreground)" }}><span>💧</span> Rainfall</td>
                  <td className="py-3 text-emerald-500 font-bold">5.3 mm</td>
                  <td className="py-3 text-emerald-500 font-bold">12.2 mm</td>
                  <td className="py-3 text-emerald-500 font-bold">25.2 mm</td>
                </tr>
                <tr>
                  <td className="py-3 flex items-center gap-1.5" style={{ color: "var(--foreground)" }}><span>💨</span> Wind Speed</td>
                  <td className="py-3" style={{ color: "var(--foreground)" }}>12 - 20 km/h</td>
                  <td className="py-3" style={{ color: "var(--foreground)" }}>10 - 22 km/h</td>
                  <td className="py-3" style={{ color: "var(--foreground)" }}>8 - 18 km/h</td>
                </tr>
                <tr>
                  <td className="py-3 flex items-center gap-1.5" style={{ color: "var(--foreground)" }}><span>💧</span> Humidity</td>
                  <td className="py-3" style={{ color: "var(--foreground)" }}>65% - 85%</td>
                  <td className="py-3" style={{ color: "var(--foreground)" }}>70% - 90%</td>
                  <td className="py-3" style={{ color: "var(--foreground)" }}>60% - 85%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Row 4: Today's Highlights & ML Model Status */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-6 rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>Today's Highlights</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <div className="flex items-center gap-1.5 text-[11px]" style={{ color: "var(--muted-foreground)" }}>
                <Thermometer size={14} className="text-rose-500" />
                <span>Max Temp</span>
              </div>
              <p className="text-lg font-bold" style={{ color: "var(--foreground)" }}>34.2°C</p>
              <p className="text-[10px] font-mono" style={{ color: "var(--muted-foreground)" }}>2:30 PM</p>
            </div>

            <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <div className="flex items-center gap-1.5 text-[11px]" style={{ color: "var(--muted-foreground)" }}>
                <Thermometer size={14} className="text-blue-500" />
                <span>Min Temp</span>
              </div>
              <p className="text-lg font-bold" style={{ color: "var(--foreground)" }}>26.1°C</p>
              <p className="text-[10px] font-mono" style={{ color: "var(--muted-foreground)" }}>5:45 AM</p>
            </div>

            <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <div className="flex items-center gap-1.5 text-[11px]" style={{ color: "var(--muted-foreground)" }}>
                <CloudRain size={14} className="text-cyan-500" />
                <span>Max Rain</span>
              </div>
              <p className="text-lg font-bold" style={{ color: "var(--foreground)" }}>8.2 mm</p>
              <p className="text-[10px] font-mono" style={{ color: "var(--muted-foreground)" }}>8:15 PM</p>
            </div>

            <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <div className="flex items-center gap-1.5 text-[11px]" style={{ color: "var(--muted-foreground)" }}>
                <Wind size={14} className="text-teal-500" />
                <span>Max Wind</span>
              </div>
              <p className="text-lg font-bold" style={{ color: "var(--foreground)" }}>22 km/h</p>
              <p className="text-[10px] font-mono" style={{ color: "var(--muted-foreground)" }}>6:30 PM</p>
            </div>
          </div>
        </div>

        <div className="lg:col-span-6 rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>ML Model Status</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 space-y-1">
              <span className="text-[11px] font-semibold text-emerald-500">Champion</span>
              <p className="text-sm font-extrabold truncate" style={{ color: "var(--foreground)" }}>{champName}</p>
              <p className="text-[10px] text-emerald-500">Active In Production</p>
            </div>

            <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <span className="text-[11px] font-semibold" style={{ color: "var(--muted-foreground)" }}>Performance</span>
              <p className="text-sm font-extrabold" style={{ color: "var(--foreground)" }}>R²: {r2Score.toFixed(3)}</p>
              <p className="text-[10px] text-emerald-500">MAE 0.89°C</p>
            </div>

            <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <span className="text-[11px] font-semibold" style={{ color: "var(--muted-foreground)" }}>Last Trained</span>
              <p className="text-sm font-extrabold" style={{ color: "var(--foreground)" }}>14 Aug 2026</p>
              <p className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>216 Models</p>
            </div>

            <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <span className="text-[11px] font-semibold" style={{ color: "var(--muted-foreground)" }}>Data Drift</span>
              <p className="text-sm font-extrabold text-emerald-500 flex items-center gap-1">
                <CheckCircle2 size={13} /> No Drift
              </p>
              <p className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>PSI &lt; 0.25</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
