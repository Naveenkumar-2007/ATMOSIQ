"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { History } from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, SERIES_COLORS, chartHeight } from "@/lib/chart-theme";

interface HistoricalRow {
  time: string;
  label: string;
  temperature_2m: number | null;
  relative_humidity_2m: number | null;
  wind_speed_10m: number | null;
  pressure_msl: number | null;
  precipitation: number | null;
  cloud_cover: number | null;
}

export default function HistoricalWeatherPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<HistoricalRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/weather/historical/${locationId}?days=${days}`);
      const rawList = Array.isArray(resp) ? resp : (resp?.observations || []);
      const rows: HistoricalRow[] = rawList.map((o: any) => ({
        time: o.time || o.observation_time,
        label: new Date(o.time || o.observation_time).toLocaleDateString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }),
        temperature_2m: o.temperature_2m ?? null,
        relative_humidity_2m: o.relative_humidity_2m ?? null,
        wind_speed_10m: o.wind_speed_10m ?? null,
        pressure_msl: o.pressure_msl ?? null,
        precipitation: o.precipitation ?? null,
        cloud_cover: o.cloud_cover ?? null,
      }));
      setData(rows);

    } catch (e: any) {
      setError(e.message || "Failed to load historical data");
    } finally {
      setIsLoading(false);
    }
  }, [locationId, days]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load historical data" message={error} onRetry={fetchData} />;
  if (data.length === 0) return <EmptyState title="No historical data" message="No historical observations found for this location and time range." variant="data" />;

  // Downsample for charts (every 3rd point for dense data)
  const chartData = data.length > 168 ? data.filter((_, i) => i % 3 === 0) : data;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Historical Weather"
        description={`Past ${days} days · ${data.length} observations · ${currentLocation?.name || locationId}`}
        icon={<History size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <div className="flex gap-1 rounded-lg border p-0.5" style={{ borderColor: "var(--border)", background: "var(--muted)" }}>
          {[3, 7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className="px-3 py-1.5 rounded-md text-xs font-medium transition-all"
              style={days === d
                ? { background: "var(--primary)", color: "var(--primary-foreground)" }
                : { color: "var(--muted-foreground)" }
              }
            >
              {d}d
            </button>
          ))}
        </div>
      </PageHeader>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {(() => {
          const temps = data.map(d => d.temperature_2m).filter((v): v is number => v != null);
          const humids = data.map(d => d.relative_humidity_2m).filter((v): v is number => v != null);
          const winds = data.map(d => d.wind_speed_10m).filter((v): v is number => v != null);
          const rains = data.map(d => d.precipitation).filter((v): v is number => v != null);
          return [
            { label: "Avg Temp", value: temps.length ? `${(temps.reduce((a, b) => a + b, 0) / temps.length).toFixed(1)}°C` : "—", color: "var(--chart-orange)" },
            { label: "Max Temp", value: temps.length ? `${Math.max(...temps).toFixed(1)}°C` : "—", color: "var(--chart-rose)" },
            { label: "Min Temp", value: temps.length ? `${Math.min(...temps).toFixed(1)}°C` : "—", color: "var(--chart-blue)" },
            { label: "Avg Humidity", value: humids.length ? `${(humids.reduce((a, b) => a + b, 0) / humids.length).toFixed(0)}%` : "—", color: "var(--chart-violet)" },
            { label: "Max Wind", value: winds.length ? `${Math.max(...winds).toFixed(0)} km/h` : "—", color: "var(--chart-teal)" },
            { label: "Total Rain", value: rains.length ? `${rains.reduce((a, b) => a + b, 0).toFixed(1)} mm` : "—", color: "var(--chart-cyan)" },
          ].map((s) => (
            <div key={s.label} className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
              <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{s.label}</p>
              <p className="text-lg font-bold mt-1" style={{ color: s.color }}>{s.value}</p>
            </div>
          ));
        })()}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Temperature History (°C)</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <LineChart data={chartData} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="label" tick={{ fontSize: 10, fill: "var(--chart-text)" }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="°" />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="temperature_2m" stroke={SERIES_COLORS.temperature} name="Temperature" strokeWidth={1.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Humidity & Wind History</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <LineChart data={chartData} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="label" tick={{ fontSize: 10, fill: "var(--chart-text)" }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Line type="monotone" dataKey="relative_humidity_2m" stroke={SERIES_COLORS.humidity} name="Humidity (%)" strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="wind_speed_10m" stroke={SERIES_COLORS.wind} name="Wind (km/h)" strokeWidth={1.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Data Table */}
      <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="px-5 py-3 border-b flex items-center justify-between" style={{ borderColor: "var(--border)" }}>
          <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>Observation Log ({data.length} records)</h3>
        </div>
        <div className="overflow-x-auto max-h-[480px] overflow-y-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                {["Time", "Temp (°C)", "Humidity (%)", "Wind (km/h)", "Pressure (hPa)", "Rain (mm)", "Clouds (%)"].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i} style={{ borderBottom: "1px solid var(--border-subtle)" }}
                    className="transition-colors"
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                  <td className="px-4 py-2 font-medium" style={{ color: "var(--foreground)" }}>{row.label}</td>
                  <td className="px-4 py-2" style={{ color: "var(--foreground)" }}>{row.temperature_2m?.toFixed(1) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{row.relative_humidity_2m?.toFixed(0) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{row.wind_speed_10m?.toFixed(1) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{row.pressure_msl?.toFixed(0) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{row.precipitation?.toFixed(1) ?? "0.0"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{row.cloud_cover?.toFixed(0) ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
