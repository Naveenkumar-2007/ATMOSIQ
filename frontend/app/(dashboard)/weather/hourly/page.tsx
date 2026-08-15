"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { WeatherIcon } from "@/components/ui/weather-icon";
import { Clock, Thermometer } from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, Area, AreaChart, ComposedChart,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, SERIES_COLORS, chartHeight } from "@/lib/chart-theme";

interface HourlyEntry {
  time: string;
  hour: string;
  temperature_2m: number | null;
  apparent_temperature: number | null;
  relative_humidity_2m: number | null;
  precipitation: number | null;
  precipitation_probability: number | null;
  wind_speed_10m: number | null;
  wind_direction_10m: number | null;
  cloud_cover: number | null;
  weather_code?: number;
}

function parseHourLabel(isoStr: string): string {
  const d = new Date(isoStr);
  return d.toLocaleTimeString("en-IN", { hour: "numeric", hour12: true });
}

function weatherCondition(code: number): string {
  if (code === 0) return "Clear";
  if (code <= 2) return "Partly Cloudy";
  if (code === 3) return "Overcast";
  if (code <= 59) return "Drizzle";
  if (code <= 69) return "Rain";
  if (code <= 79) return "Snow";
  return "Stormy";
}

type MetricTab = "temperature" | "feelsLike" | "rainProb" | "rainfall" | "wind" | "humidity";

export default function HourlyForecastPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<HourlyEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hours, setHours] = useState(24);
  const [activeMetric, setActiveMetric] = useState<MetricTab>("temperature");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const combined = await apiClient<any>(`/api/v1/weather/combined/${locationId}`);
      const h = combined.hourly;
      if (!h || !h.times || h.times.length === 0) {
        setData([]);
        return;
      }
      const entries: HourlyEntry[] = h.times.slice(0, hours).map((t: string, i: number) => ({
        time: t,
        hour: parseHourLabel(t),
        temperature_2m: h.temperature_2m?.[i] ?? null,
        apparent_temperature: h.apparent_temperature?.[i] ?? null,
        relative_humidity_2m: h.relative_humidity_2m?.[i] ?? null,
        precipitation: h.precipitation?.[i] ?? null,
        precipitation_probability: h.precipitation_probability?.[i] ?? null,
        wind_speed_10m: h.wind_speed_10m?.[i] ?? null,
        wind_direction_10m: h.wind_direction_10m?.[i] ?? null,
        cloud_cover: h.cloud_cover?.[i] ?? null,
      }));
      setData(entries);
    } catch (e: any) {
      setError(e.message || "Failed to load hourly forecast");
    } finally {
      setIsLoading(false);
    }
  }, [locationId, hours]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load hourly forecast" message={error} onRetry={fetchData} />;
  if (data.length === 0) return <EmptyState title="No hourly data" message="No hourly forecast data available for this location." variant="data" />;

  const metricTabs: { key: MetricTab; label: string }[] = [
    { key: "temperature", label: "Temperature" },
    { key: "feelsLike", label: "Feels Like" },
    { key: "rainProb", label: "Rain Probability" },
    { key: "rainfall", label: "Rainfall" },
    { key: "wind", label: "Wind" },
    { key: "humidity", label: "Humidity" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Hourly Forecast"
        description={`Next ${hours} hours · ${currentLocation?.name || locationId}`}
        icon={<Clock size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        {/* Hour range buttons */}
        <div className="flex gap-1 rounded-lg border p-0.5" style={{ borderColor: "var(--border)", background: "var(--muted)" }}>
          {[24, 48].map((h) => (
            <button
              key={h}
              onClick={() => setHours(h)}
              className="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
              style={hours === h
                ? { background: "var(--primary)", color: "var(--primary-foreground)" }
                : { color: "var(--muted-foreground)" }
              }
            >
              {h}h
            </button>
          ))}
        </div>
      </PageHeader>

      {/* Metric Tabs */}
      <div className="flex gap-1 flex-wrap rounded-lg border p-1" style={{ borderColor: "var(--border)", background: "var(--card)" }}>
        {metricTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveMetric(tab.key)}
            className="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
            style={activeMetric === tab.key
              ? { background: "var(--primary)", color: "var(--primary-foreground)" }
              : { color: "var(--muted-foreground)" }
            }
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Hourly Cards Strip */}
      <div className="overflow-x-auto pb-2">
        <div className="flex gap-3" style={{ minWidth: "max-content" }}>
          {data.slice(0, 24).map((entry, i) => (
            <div
              key={i}
              className="flex flex-col items-center gap-1.5 rounded-xl border px-3 py-3 min-w-[72px] text-center"
              style={{ background: "var(--card)", borderColor: "var(--card-border)" }}
            >
              <span className="text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>{entry.hour}</span>
              <WeatherIcon code={entry.weather_code ?? (entry.precipitation && entry.precipitation > 0.5 ? 61 : entry.cloud_cover && entry.cloud_cover > 70 ? 3 : 1)} size={22} />
              <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
                {entry.temperature_2m?.toFixed(0)}°
              </span>
              <span className="text-[10px]" style={{ color: "var(--chart-blue)" }}>
                {entry.precipitation_probability?.toFixed(0) ?? "—"}%
              </span>
              <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>
                {entry.wind_speed_10m?.toFixed(0)} km/h
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Temperature Chart */}
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Temperature Forecast (°C)</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <AreaChart data={data} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="hour" tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="°" />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Area type="monotone" dataKey="temperature_2m" stroke={SERIES_COLORS.temperature} fill={SERIES_COLORS.temperature} fillOpacity={0.1} name="Temperature (°C)" strokeWidth={2} />
              <Area type="monotone" dataKey="apparent_temperature" stroke={SERIES_COLORS.forecast} fill="none" strokeDasharray="4 4" name="Feels Like (°C)" strokeWidth={1.5} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Rain Chart */}
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Rain Probability (%) & Rainfall (mm)</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <ComposedChart data={data} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="hour" tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <YAxis yAxisId="prob" tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="%" domain={[0, 100]} />
              <YAxis yAxisId="mm" orientation="right" tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="mm" />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Line yAxisId="prob" type="monotone" dataKey="precipitation_probability" stroke={SERIES_COLORS.rainProbability} name="Rain Probability (%)" strokeWidth={2} dot={false} />
              <Bar yAxisId="mm" dataKey="precipitation" fill={SERIES_COLORS.rainfall} name="Rainfall (mm)" radius={[2, 2, 0, 0]} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Wind Chart */}
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Wind Speed (km/h)</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <AreaChart data={data} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="hour" tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit=" km/h" />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Area type="monotone" dataKey="wind_speed_10m" stroke={SERIES_COLORS.wind} fill={SERIES_COLORS.wind} fillOpacity={0.1} name="Wind Speed (km/h)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Humidity Chart */}
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Humidity (%)</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <AreaChart data={data} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="hour" tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="%" domain={[0, 100]} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Area type="monotone" dataKey="relative_humidity_2m" stroke={SERIES_COLORS.humidity} fill={SERIES_COLORS.humidity} fillOpacity={0.1} name="Humidity (%)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Hourly Detail Table */}
      <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--muted)" }}>
                {["Time", "Temp (°C)", "Feels Like", "Rain Prob", "Rain (mm)", "Wind", "Humidity", "Clouds"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((entry, i) => (
                <tr key={i} className="transition-colors" style={{ borderBottom: "1px solid var(--border-subtle)" }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                  <td className="px-4 py-2.5 font-medium" style={{ color: "var(--foreground)" }}>{entry.hour}</td>
                  <td className="px-4 py-2.5 font-semibold" style={{ color: "var(--foreground)" }}>{entry.temperature_2m?.toFixed(1) ?? "—"}</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{entry.apparent_temperature?.toFixed(1) ?? "—"}</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--chart-blue)" }}>{entry.precipitation_probability?.toFixed(0) ?? "—"}%</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{entry.precipitation?.toFixed(1) ?? "0.0"}</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{entry.wind_speed_10m?.toFixed(0) ?? "—"} km/h</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{entry.relative_humidity_2m?.toFixed(0) ?? "—"}%</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{entry.cloud_cover?.toFixed(0) ?? "—"}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
