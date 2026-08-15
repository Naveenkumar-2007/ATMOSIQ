"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { WeatherIcon } from "@/components/ui/weather-icon";
import { CalendarDays, ArrowUp, ArrowDown, Droplets, Wind } from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ComposedChart, Line,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, SERIES_COLORS, chartHeight } from "@/lib/chart-theme";

interface DailyEntry {
  date: string;
  dayLabel: string;
  weather_code: number;
  temperature_max: number | null;
  temperature_min: number | null;
  precipitation_sum: number | null;
  precipitation_probability_max: number | null;
  wind_speed_max: number | null;
  wind_gusts_max: number | null;
  sunrise: string;
  sunset: string;
}

function dayLabel(dateStr: string, index: number): string {
  if (index === 0) return "Today";
  if (index === 1) return "Tomorrow";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" });
}

function weatherCondition(code: number): string {
  if (code === 0) return "Clear Sky";
  if (code <= 2) return "Partly Cloudy";
  if (code === 3) return "Overcast";
  if (code <= 49) return "Foggy";
  if (code <= 59) return "Drizzle";
  if (code <= 69) return "Rain";
  if (code <= 79) return "Snow";
  return "Thunderstorm";
}

export default function DailyForecastPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<DailyEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const combined = await apiClient<any>(`/api/v1/weather/combined/${locationId}`);
      const d = combined.daily;
      if (!d || !d.dates || d.dates.length === 0) {
        setData([]);
        return;
      }
      const entries: DailyEntry[] = d.dates.map((date: string, i: number) => ({
        date,
        dayLabel: dayLabel(date, i),
        weather_code: d.weather_code?.[i] ?? 0,
        temperature_max: d.temperature_max?.[i] ?? null,
        temperature_min: d.temperature_min?.[i] ?? null,
        precipitation_sum: d.precipitation_sum?.[i] ?? null,
        precipitation_probability_max: d.precipitation_probability_max?.[i] ?? null,
        wind_speed_max: d.wind_speed_max?.[i] ?? null,
        wind_gusts_max: d.wind_gusts_max?.[i] ?? null,
        sunrise: d.sunrise?.[i] ?? "",
        sunset: d.sunset?.[i] ?? "",
      }));
      setData(entries);
    } catch (e: any) {
      setError(e.message || "Failed to load daily forecast");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load daily forecast" message={error} onRetry={fetchData} />;
  if (data.length === 0) return <EmptyState title="No daily data" variant="data" />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Daily Forecast"
        description={`${data.length}-day outlook · ${currentLocation?.name || locationId}`}
        icon={<CalendarDays size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      />

      {/* Daily Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {data.map((day, i) => (
          <div
            key={i}
            className="rounded-xl border p-4 transition-all hover:shadow-md"
            style={{ background: "var(--card)", borderColor: "var(--card-border)" }}
          >
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>{day.dayLabel}</p>
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>{day.date}</p>
              </div>
              <WeatherIcon code={day.weather_code} size={28} />
            </div>
            <p className="text-xs font-medium mb-3" style={{ color: "var(--muted-foreground)" }}>
              {weatherCondition(day.weather_code)}
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex items-center gap-1.5">
                <ArrowUp size={12} style={{ color: "var(--chart-rose)" }} />
                <span style={{ color: "var(--muted-foreground)" }}>High</span>
                <span className="font-semibold ml-auto" style={{ color: "var(--foreground)" }}>{day.temperature_max?.toFixed(1) ?? "—"}°</span>
              </div>
              <div className="flex items-center gap-1.5">
                <ArrowDown size={12} style={{ color: "var(--chart-blue)" }} />
                <span style={{ color: "var(--muted-foreground)" }}>Low</span>
                <span className="font-semibold ml-auto" style={{ color: "var(--foreground)" }}>{day.temperature_min?.toFixed(1) ?? "—"}°</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Droplets size={12} style={{ color: "var(--chart-cyan)" }} />
                <span style={{ color: "var(--muted-foreground)" }}>Rain</span>
                <span className="font-semibold ml-auto" style={{ color: "var(--foreground)" }}>{day.precipitation_probability_max?.toFixed(0) ?? "—"}%</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Wind size={12} style={{ color: "var(--chart-teal)" }} />
                <span style={{ color: "var(--muted-foreground)" }}>Wind</span>
                <span className="font-semibold ml-auto" style={{ color: "var(--foreground)" }}>{day.wind_speed_max?.toFixed(0) ?? "—"}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Temperature Range */}
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Temperature Range (°C)</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <ComposedChart data={data} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="dayLabel" tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="°" />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Bar dataKey="temperature_max" fill="var(--chart-rose)" name="High (°C)" radius={[4, 4, 0, 0]} barSize={16} />
              <Bar dataKey="temperature_min" fill="var(--chart-blue)" name="Low (°C)" radius={[4, 4, 0, 0]} barSize={16} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Precipitation Outlook */}
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Precipitation Outlook</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <ComposedChart data={data} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="dayLabel" tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <YAxis yAxisId="prob" tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="%" domain={[0, 100]} />
              <YAxis yAxisId="mm" orientation="right" tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="mm" />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Line yAxisId="prob" type="monotone" dataKey="precipitation_probability_max" stroke={SERIES_COLORS.rainProbability} name="Max Prob (%)" strokeWidth={2} />
              <Bar yAxisId="mm" dataKey="precipitation_sum" fill={SERIES_COLORS.rainfall} name="Total Rain (mm)" radius={[4, 4, 0, 0]} barSize={20} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Data Table */}
      <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--muted)" }}>
                {["Day", "Condition", "High", "Low", "Rain Prob", "Rain Total", "Wind Max", "Gust Max"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((day, i) => (
                <tr key={i} style={{ borderBottom: "1px solid var(--border-subtle)" }}
                    className="transition-colors"
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                  <td className="px-4 py-2.5 font-medium" style={{ color: "var(--foreground)" }}>{day.dayLabel}</td>
                  <td className="px-4 py-2.5 flex items-center gap-2">
                    <WeatherIcon code={day.weather_code} size={16} />
                    <span style={{ color: "var(--muted-foreground)" }}>{weatherCondition(day.weather_code)}</span>
                  </td>
                  <td className="px-4 py-2.5 font-semibold" style={{ color: "var(--chart-rose)" }}>{day.temperature_max?.toFixed(1) ?? "—"}°C</td>
                  <td className="px-4 py-2.5 font-semibold" style={{ color: "var(--chart-blue)" }}>{day.temperature_min?.toFixed(1) ?? "—"}°C</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{day.precipitation_probability_max?.toFixed(0) ?? "—"}%</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{day.precipitation_sum?.toFixed(1) ?? "0.0"} mm</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{day.wind_speed_max?.toFixed(0) ?? "—"} km/h</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{day.wind_gusts_max?.toFixed(0) ?? "—"} km/h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
