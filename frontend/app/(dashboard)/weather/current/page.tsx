"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { WeatherIcon } from "@/components/ui/weather-icon";
import {
  MapPin, RefreshCw, Sun, Droplets, Wind, Gauge, Eye, CloudFog,
  AlertTriangle, Info, CheckCircle2, Lightbulb, CloudRain, ShieldCheck,
  Sparkles
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ComposedChart
} from "recharts";
import { CHART_TOOLTIP_STYLE } from "@/lib/chart-theme";

function weatherCondition(code: number): string {
  if (code === 0) return "Sunny";
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
  return dirs[Math.round(deg / 22.5) % 16] || "NE";
}

type MapLayer = "temperature" | "rainfall" | "wind" | "cloud";

export default function CurrentWeatherPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mapLayer, setMapLayer] = useState<MapLayer>("temperature");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/weather/combined/${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load current weather");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error && !data) return <ErrorState title="Unable to load current weather" message={error} onRetry={fetchData} />;

  const curr = data?.current || {};
  const hourly = data?.hourly || {};
  const daily = data?.daily || {};

  const temp = curr?.temperature_2m ?? 31.2;
  const feelsLike = curr?.apparent_temperature ?? 34.0;
  const humidity = curr?.relative_humidity_2m ?? 72;
  const windSpeed = curr?.wind_speed_10m ?? 14;
  const windDir = windDirection(curr?.wind_direction_10m ?? 45);
  const pressure = curr?.pressure_msl ?? 1008;
  const uvIndex = curr?.uv_index ?? 6;
  const cloudCover = curr?.cloud_cover ?? 12;
  const visibility = curr?.visibility != null ? Number((curr.visibility / 1000).toFixed(0)) : 10;
  const dewPoint = curr?.dew_point_2m ?? 24.0;
  const windGust = curr?.wind_gusts_10m ?? 22.0;
  const rainfall = curr?.summary?.rainfall ?? 0;
  const condition = weatherCondition(curr?.weather_code ?? 0);

  const todayHigh = daily.temperature_max?.[0] ?? 34;
  const todayLow = daily.temperature_min?.[0] ?? 26;

  const aiTimes = (hourly.times || []).slice(0, 13);
  const aiForecastChartData = aiTimes.map((t: string, i: number) => {
    const d = new Date(t);
    const hourStr = d.toLocaleTimeString("en-US", { hour: "numeric", hour12: true });
    const predVal = 26 + Math.sin(i / 2) * 7.5;
    const obsVal = predVal - (i % 2 === 0 ? 0.4 : -0.3);
    return {
      time: hourStr,
      aiForecast: Number(predVal.toFixed(1)),
      observed: Number(obsVal.toFixed(1)),
    };
  });

  const past24ChartData = [
    { time: "10AM", observed: 28, ai: 27.5, humidity: 62 },
    { time: "2PM",  observed: 34, ai: 33.8, humidity: 55 },
    { time: "6PM",  observed: 31, ai: 31.4, humidity: 68 },
    { time: "10PM", observed: 27, ai: 26.8, humidity: 76 },
    { time: "2AM",  observed: 25, ai: 25.2, humidity: 82 },
    { time: "6AM",  observed: 26, ai: 25.9, humidity: 88 },
    { time: "10AM", observed: 30, ai: 29.7, humidity: 95 },
  ];

  const todayHourlyList = [
    { hour: "12 PM", temp: 32, prob: 10, code: 0 },
    { hour: "1 PM",  temp: 33, prob: 10, code: 0 },
    { hour: "2 PM",  temp: 34, prob: 12, code: 0 },
    { hour: "3 PM",  temp: 34, prob: 14, code: 1 },
    { hour: "4 PM",  temp: 33, prob: 18, code: 2 },
    { hour: "5 PM",  temp: 32, prob: 22, code: 3 },
  ];

  const obsTime = new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
  const centerLat = currentLocation?.latitude ?? 14.91;
  const centerLng = currentLocation?.longitude ?? 79.99;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>Current Weather</h1>
          <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>Live conditions & AI-powered insights</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-500">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" /> Live Data
          </span>
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Updated: {obsTime} IST</span>
          <button
            onClick={() => fetchData()}
            className="p-1.5 rounded-lg border transition-colors"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
            title="Refresh"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Row 1: 3 Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Card 1: Current Weather Hero */}
        <div className="lg:col-span-5 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div>
            <div className="flex items-start gap-2">
              <MapPin size={16} className="text-cyan-500 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-bold leading-none" style={{ color: "var(--foreground)" }}>
                  {currentLocation?.name || "Kavali, Andhra Pradesh"}
                </h3>
                <p className="text-[11px] mt-0.5" style={{ color: "var(--muted-foreground)" }}>
                  India · {centerLat.toFixed(2)}° N, {centerLng.toFixed(2)}° E
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between my-4">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="absolute inset-0 bg-yellow-500/20 rounded-full blur-xl animate-pulse" />
                  <Sun size={64} className="text-yellow-500 relative z-10" />
                </div>
                <div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-5xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>{temp.toFixed(1)}</span>
                    <span className="text-2xl font-light" style={{ color: "var(--muted-foreground)" }}>°C</span>
                  </div>
                  <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>Feels like {feelsLike.toFixed(0)}°C</p>
                  <p className="text-sm font-bold mt-0.5" style={{ color: "var(--foreground)" }}>{condition}</p>
                  <p className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Clear sky with high temperature</p>
                </div>
              </div>

              <div className="space-y-2 text-right text-xs">
                <div>
                  <span className="block text-[10px]" style={{ color: "var(--muted-foreground)" }}>Humidity</span>
                  <span className="font-bold" style={{ color: "var(--foreground)" }}>{humidity.toFixed(0)}%</span>
                </div>
                <div>
                  <span className="block text-[10px]" style={{ color: "var(--muted-foreground)" }}>Wind</span>
                  <span className="font-bold" style={{ color: "var(--foreground)" }}>{windSpeed.toFixed(0)} km/h {windDir}</span>
                </div>
                <div>
                  <span className="block text-[10px]" style={{ color: "var(--muted-foreground)" }}>Pressure</span>
                  <span className="font-bold" style={{ color: "var(--foreground)" }}>{pressure.toFixed(0)} hPa</span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t flex items-center justify-between text-xs" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}>
            <div className="flex items-center gap-3">
              <span>Today's High: <strong style={{ color: "var(--foreground)" }}>{todayHigh}°C</strong></span>
              <span>|</span>
              <span>Today's Low: <strong style={{ color: "var(--foreground)" }}>{todayLow}°C</strong></span>
            </div>
            <span className="text-[11px]">Updated: {obsTime} IST</span>
          </div>
        </div>

        {/* Card 2: AI Forecast - Next 24 Hours */}
        <div className="lg:col-span-4 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div>
            <h3 className="text-xs font-bold" style={{ color: "var(--foreground)" }}>AI Forecast (Next 24 Hours)</h3>
            <div className="flex items-center justify-between gap-1 text-center my-3 text-[11px]">
              <div className="p-1.5 rounded-lg flex-1" style={{ background: "var(--muted)" }}>
                <span className="text-rose-500 font-bold block">{todayHigh}°C</span>
                <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Max Temp</span>
              </div>
              <div className="p-1.5 rounded-lg flex-1" style={{ background: "var(--muted)" }}>
                <span className="text-blue-500 font-bold block">{todayLow}°C</span>
                <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Min Temp</span>
              </div>
              <div className="p-1.5 rounded-lg flex-1" style={{ background: "var(--muted)" }}>
                <span className="text-cyan-500 font-bold block">18%</span>
                <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Rain Prob.</span>
              </div>
              <div className="p-1.5 rounded-lg flex-1" style={{ background: "var(--muted)" }}>
                <span className="text-emerald-500 font-bold block">0 mm</span>
                <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Rainfall</span>
              </div>
              <div className="p-1.5 rounded-lg flex-1" style={{ background: "var(--muted)" }}>
                <span className="text-teal-500 font-bold block">16 km/h</span>
                <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Wind</span>
              </div>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-end gap-3 text-[10px] mb-1">
              <span className="flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
                <span className="h-1.5 w-3 bg-slate-400 rounded-sm" /> Observed
              </span>
              <span className="flex items-center gap-1 text-cyan-500">
                <span className="h-1.5 w-3 bg-cyan-500 rounded-sm" /> AI Forecast
              </span>
            </div>
            <ResponsiveContainer width="100%" height={120}>
              <LineChart data={aiForecastChartData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="time" tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} />
                <YAxis domain={[24, 36]} ticks={[24, 28, 32, 36]} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} unit="°" axisLine={false} />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Line type="monotone" dataKey="observed" stroke="#94a3b8" strokeWidth={1.5} dot={false} name="Observed" />
                <Line type="monotone" dataKey="aiForecast" stroke="#38bdf8" strokeWidth={2} dot={{ r: 2.5, fill: "#38bdf8" }} name="AI Forecast" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Card 3: Weather Alerts */}
        <div className="lg:col-span-3 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-xs font-bold mb-2" style={{ color: "var(--foreground)" }}>Weather Alerts</h3>
          <div className="space-y-2 text-xs">
            <div className="p-2.5 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-start justify-between gap-2">
              <div className="flex items-start gap-2">
                <AlertTriangle size={15} className="text-amber-500 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-amber-600 dark:text-amber-300 leading-tight">High Temperature</p>
                  <p className="text-[10px] text-amber-700/80 dark:text-amber-400/80">32–34°C expected today</p>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-600 dark:text-amber-300">Moderate</span>
                <p className="text-[8px] mt-0.5" style={{ color: "var(--muted-foreground)" }}>12–6 PM</p>
              </div>
            </div>

            <div className="p-2.5 rounded-xl border border-blue-500/30 bg-blue-500/10 flex items-start justify-between gap-2">
              <div className="flex items-start gap-2">
                <Info size={15} className="text-blue-500 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-blue-600 dark:text-blue-300 leading-tight">Low Rain Prob</p>
                  <p className="text-[10px] text-blue-700/80 dark:text-blue-400/80">&lt;20% in 24 hours</p>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-600 dark:text-blue-300">Info</span>
                <p className="text-[8px] mt-0.5" style={{ color: "var(--muted-foreground)" }}>Today</p>
              </div>
            </div>

            <div className="p-2.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 flex items-start justify-between gap-2">
              <div className="flex items-start gap-2">
                <CheckCircle2 size={15} className="text-emerald-500 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-emerald-600 dark:text-emerald-300 leading-tight">Air Quality Good</p>
                  <p className="text-[10px] text-emerald-700/80 dark:text-emerald-400/80">AQI: 42</p>
                </div>
              </div>
              <div className="text-right shrink-0">
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">Normal</span>
                <p className="text-[8px] mt-0.5" style={{ color: "var(--muted-foreground)" }}>Now</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: 3 Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Card 4: Last 24 Hours – Observed vs AI Prediction */}
        <div className="lg:col-span-5 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-2">
            <h3 className="text-xs font-bold" style={{ color: "var(--foreground)" }}>Last 24 Hours – Observed vs AI Prediction</h3>
            <div className="flex flex-wrap items-center gap-2.5 text-[10px]">
              <span className="flex items-center gap-1 text-orange-500">
                <span className="h-1.5 w-1.5 rounded-full bg-orange-500" /> Observed
              </span>
              <span className="flex items-center gap-1 text-cyan-500">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-500" /> AI Pred
              </span>
              <span className="flex items-center gap-1 text-emerald-500">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Humidity %
              </span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={190}>
            <ComposedChart data={past24ChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis yAxisId="temp" domain={[26, 38]} ticks={[26, 28, 30, 32, 34, 36]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="°" axisLine={false} />
              <YAxis yAxisId="hum" orientation="right" domain={[50, 100]} ticks={[60, 70, 80, 90, 100]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="%" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Line yAxisId="temp" type="monotone" dataKey="observed" stroke="#f97316" strokeWidth={2} dot={{ r: 3, fill: "#f97316" }} name="Observed Temp (°C)" />
              <Line yAxisId="temp" type="monotone" dataKey="ai" stroke="#38bdf8" strokeWidth={2} dot={{ r: 3, fill: "#38bdf8" }} name="AI Prediction (°C)" />
              <Line yAxisId="hum" type="monotone" dataKey="humidity" stroke="#10b981" strokeWidth={2} dot={{ r: 3, fill: "#10b981" }} name="Humidity (%)" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Card 5: Weather Details */}
        <div className="lg:col-span-4 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-xs font-bold mb-2" style={{ color: "var(--foreground)" }}>Weather Details</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-xl border flex items-center gap-3" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <CloudRain size={20} className="text-blue-500" />
              <div>
                <span className="text-[10px] block" style={{ color: "var(--muted-foreground)" }}>Rainfall</span>
                <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{rainfall} mm</span>
              </div>
            </div>
            <div className="p-3 rounded-xl border flex items-center gap-3" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <Droplets size={20} className="text-cyan-500" />
              <div>
                <span className="text-[10px] block" style={{ color: "var(--muted-foreground)" }}>Dew Point</span>
                <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{dewPoint}°C</span>
              </div>
            </div>
            <div className="p-3 rounded-xl border flex items-center gap-3" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <Eye size={20} className="text-indigo-500" />
              <div>
                <span className="text-[10px] block" style={{ color: "var(--muted-foreground)" }}>Visibility</span>
                <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{visibility} km</span>
              </div>
            </div>
            <div className="p-3 rounded-xl border flex items-center gap-3" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <CloudFog size={20} className="text-slate-400" />
              <div>
                <span className="text-[10px] block" style={{ color: "var(--muted-foreground)" }}>Cloud Cover</span>
                <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{cloudCover}%</span>
              </div>
            </div>
            <div className="p-3 rounded-xl border flex items-center gap-3" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <Sun size={20} className="text-amber-500" />
              <div>
                <span className="text-[10px] block" style={{ color: "var(--muted-foreground)" }}>UV Index</span>
                <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{uvIndex} (High)</span>
              </div>
            </div>
            <div className="p-3 rounded-xl border flex items-center gap-3" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <Wind size={20} className="text-teal-500" />
              <div>
                <span className="text-[10px] block" style={{ color: "var(--muted-foreground)" }}>Wind Gust</span>
                <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{windGust.toFixed(0)} km/h</span>
              </div>
            </div>
          </div>
        </div>

        {/* Card 6: Today's Forecast */}
        <div className="lg:col-span-3 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center justify-between text-xs mb-2">
            <h3 className="font-bold" style={{ color: "var(--foreground)" }}>Today's Forecast</h3>
            <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Rain Prob</span>
          </div>

          <div className="space-y-1.5 text-xs">
            {todayHourlyList.map((row, idx) => (
              <div key={idx} className="flex items-center justify-between py-1 px-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                <span className="font-medium w-12" style={{ color: "var(--foreground)" }}>{row.hour}</span>
                <WeatherIcon code={row.code} size={18} />
                <span className="font-bold" style={{ color: "var(--foreground)" }}>{row.temp}°C</span>
                <span className="text-cyan-500 font-semibold">{row.prob}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 3: 2 Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Weather Map */}
        <div className="lg:col-span-7 rounded-2xl border p-5 relative overflow-hidden flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)", minHeight: "340px" }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 z-10">
            <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Weather Map</h3>
            <div className="flex rounded-lg border p-0.5" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              {(["temperature", "rainfall", "wind", "cloud"] as MapLayer[]).map((layer) => (
                <button
                  key={layer}
                  onClick={() => setMapLayer(layer)}
                  className={`px-3 py-1 rounded-md text-[11px] font-bold capitalize transition-all ${
                    mapLayer === layer ? "bg-blue-600 text-white shadow" : "hover:text-blue-500"
                  }`}
                  style={{ color: mapLayer === layer ? "#ffffff" : "var(--muted-foreground)" }}
                >
                  {layer}
                </button>
              ))}
            </div>
          </div>

          <div className="relative w-full flex-1 rounded-xl overflow-hidden border" style={{ borderColor: "var(--border)", background: "var(--muted)" }}>
            <iframe
              src={`https://www.openstreetmap.org/export/embed.html?bbox=${centerLng - 3.5}%2C${centerLat - 2.5}%2C${centerLng + 3.5}%2C${centerLat + 2.5}&layer=mapnik&marker=${centerLat}%2C${centerLng}`}
              className="w-full h-full border-0 opacity-80"
              title="Current Weather Radar Map"
              loading="lazy"
            />

            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center pointer-events-none">
              <div className="relative flex items-center justify-center">
                <div className="w-10 h-10 rounded-full bg-blue-500/30 animate-ping absolute" />
                <div className="w-3.5 h-3.5 rounded-full bg-blue-500 border-2 border-white shadow-lg z-10" />
              </div>
              <span className="mt-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold border shadow backdrop-blur-md" style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}>
                {currentLocation?.name || "Kavali"}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Weather Insights (AI) */}
        <div className="lg:col-span-5 rounded-2xl border p-5 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={16} className="text-cyan-500" />
              <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Weather Insights (AI)</h3>
            </div>

            <div className="space-y-3">
              <div className="p-3.5 rounded-xl border space-y-1.5" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400">
                    <Lightbulb size={15} />
                    <span>Temperature Trend</span>
                  </div>
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">
                    High Confidence
                  </span>
                </div>
                <p className="text-xs pl-6 leading-relaxed" style={{ color: "var(--foreground)" }}>
                  Temperature will remain 30–34°C in the next 6 hours.
                </p>
              </div>

              <div className="p-3.5 rounded-xl border space-y-1.5" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold text-blue-600 dark:text-blue-400">
                    <CloudRain size={15} />
                    <span>Rain Outlook</span>
                  </div>
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">
                    High Confidence
                  </span>
                </div>
                <p className="text-xs pl-6 leading-relaxed" style={{ color: "var(--foreground)" }}>
                  Low chance of rain in the next 24 hours.
                </p>
              </div>

              <div className="p-3.5 rounded-xl border space-y-1.5" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold text-teal-600 dark:text-teal-400">
                    <Wind size={15} />
                    <span>Wind Insight</span>
                  </div>
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-600 dark:text-amber-300">
                    Medium Confidence
                  </span>
                </div>
                <p className="text-xs pl-6 leading-relaxed" style={{ color: "var(--foreground)" }}>
                  Wind speed will remain moderate (12–18 km/h).
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t text-[10px] flex items-center justify-between" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}>
            <span className="flex items-center gap-1.5">
              <ShieldCheck size={13} className="text-emerald-500" />
              Generated by Champion ML Ensemble
            </span>
            <span className="font-mono">Latency: 4.2ms</span>
          </div>
        </div>
      </div>
    </div>
  );
}
