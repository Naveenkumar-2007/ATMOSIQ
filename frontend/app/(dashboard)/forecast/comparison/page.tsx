"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { EmptyState } from "@/components/common/empty-state";
import { GitCompareArrows } from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, CHART_PALETTE, chartHeight } from "@/lib/chart-theme";

export default function ForecastComparisonPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/forecast/comparison?location=${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load forecast comparison");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load forecast comparison" message={error} onRetry={fetchData} />;
  if (!data) return <EmptyState title="No comparison data" variant="predictions" />;

  const timeseries = data.timeseries || [];
  const models = data.models || [];
  const chartData = timeseries.map((entry: any) => ({
    time: new Date(entry.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit" }),
    observed: entry.observed,
    ...Object.fromEntries((entry.forecasts || []).map((f: any) => [f.model, f.value])),
  }));
  const modelNames = models.map((m: any) => m.model_name || m.name || m);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Forecast Comparison"
        description={`Provider forecast vs ML prediction vs observation · ${currentLocation?.name || locationId}`}
        icon={<GitCompareArrows size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      />

      {/* Summary Cards */}
      {models.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {models.map((m: any, i: number) => (
            <div key={i} className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
              <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{m.model_name || m.name || `Model ${i + 1}`}</p>
              <p className="text-lg font-bold mt-1" style={{ color: CHART_PALETTE[i % CHART_PALETTE.length] }}>
                {m.mae != null ? `MAE ${m.mae.toFixed(2)}` : m.metric_value != null ? m.metric_value.toFixed(2) : "—"}
              </p>
              {m.bias != null && (
                <p className="text-xs mt-1" style={{ color: "var(--muted-foreground)" }}>Bias: {m.bias > 0 ? "+" : ""}{m.bias.toFixed(2)}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Comparison Chart */}
      {chartData.length > 0 ? (
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Forecast vs Observed</h3>
          <ResponsiveContainer width="100%" height={chartHeight("lg")}>
            <LineChart data={chartData} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--chart-text)" }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Line type="monotone" dataKey="observed" stroke="var(--chart-emerald)" name="Observed" strokeWidth={2.5} dot={false} />
              {modelNames.map((name: string, i: number) => (
                <Line key={name} type="monotone" dataKey={name} stroke={CHART_PALETTE[(i + 1) % CHART_PALETTE.length]} name={name} strokeWidth={1.5} dot={false} strokeDasharray={i > 0 ? "4 4" : undefined} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <EmptyState title="No timeseries data" message="Forecast comparison timeseries is empty. Run predictions and verification first." variant="chart" />
      )}

      {/* Raw Data */}
      {timeseries.length > 0 && (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="px-5 py-3 border-b" style={{ borderColor: "var(--border)" }}>
            <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>Comparison Data ({timeseries.length} points)</h3>
          </div>
          <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  <th className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>Time</th>
                  <th className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--chart-emerald)" }}>Observed</th>
                  {modelNames.map((n: string) => (
                    <th key={n} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{n}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {timeseries.slice(0, 100).map((entry: any, i: number) => (
                  <tr key={i} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td className="px-4 py-2" style={{ color: "var(--foreground)" }}>{new Date(entry.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</td>
                    <td className="px-4 py-2 font-semibold" style={{ color: "var(--chart-emerald)" }}>{entry.observed?.toFixed(2) ?? "—"}</td>
                    {(entry.forecasts || []).map((f: any, j: number) => (
                      <td key={j} className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{f.value?.toFixed(2) ?? "—"}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
