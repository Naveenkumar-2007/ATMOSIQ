"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { ClipboardCheck, Filter, ChevronLeft, ChevronRight } from "lucide-react";
import {
  ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ZAxis,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, chartHeight } from "@/lib/chart-theme";

export default function ForecastVerificationPage() {
  const { locationId } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [taskFilter, setTaskFilter] = useState<string>("");
  const [page, setPage] = useState(0);
  const limit = 100;

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (locationId) params.set("location", locationId);
      if (taskFilter) params.set("task", taskFilter);
      params.set("limit", limit.toString());
      params.set("offset", (page * limit).toString());
      const resp = await apiClient<any>(`/api/v1/ml/verification?${params}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load verification data");
    } finally {
      setIsLoading(false);
    }
  }, [locationId, taskFilter, page]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load verification" message={error} onRetry={fetchData} />;

  const rows = data?.rows || [];
  const total = data?.total || 0;
  const summary = data?.summary || {};
  const totalPages = Math.ceil(total / limit);

  const scatterData = rows.filter((r: any) => r.forecast_value != null && r.actual_value != null).map((r: any) => ({
    forecast: r.forecast_value,
    actual: r.actual_value,
  }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Forecast Verification"
        description={`${total} verified forecasts`}
        icon={<ClipboardCheck size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <select
          value={taskFilter}
          onChange={(e) => { setTaskFilter(e.target.value); setPage(0); }}
          className="text-xs rounded-lg border px-3 py-1.5 font-medium"
          style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
        >
          <option value="">All Tasks</option>
          {["temperature", "humidity", "pressure", "wind_speed", "precipitation_amount", "rain_occurrence"].map((t) => (
            <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
          ))}
        </select>
      </PageHeader>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MC label="Total Forecasts" value={summary.total_forecasts?.toLocaleString() || "0"} color="var(--primary)" />
        <MC label="MAE" value={summary.mae != null ? summary.mae.toFixed(4) : "—"} color="var(--chart-emerald)" />
        <MC label="RMSE" value={summary.rmse != null ? summary.rmse.toFixed(4) : "—"} color="var(--chart-amber)" />
        <MC label="Bias" value={summary.bias != null ? `${summary.bias > 0 ? "+" : ""}${summary.bias.toFixed(4)}` : "—"} color="var(--chart-violet)" />
      </div>

      {/* Scatter Plot */}
      {scatterData.length > 0 && (
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Forecast vs Actual (Scatter)</h3>
          <ResponsiveContainer width="100%" height={chartHeight("lg")}>
            <ScatterChart margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis type="number" dataKey="forecast" name="Forecast" tick={{ fontSize: 11, fill: "var(--chart-text)" }} label={{ value: "Forecast", position: "bottom", fill: "var(--chart-text)", fontSize: 11 }} />
              <YAxis type="number" dataKey="actual" name="Actual" tick={{ fontSize: 11, fill: "var(--chart-text)" }} label={{ value: "Actual", angle: -90, position: "insideLeft", fill: "var(--chart-text)", fontSize: 11 }} />
              <ZAxis range={[20, 20]} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Scatter data={scatterData} fill="var(--chart-blue)" fillOpacity={0.6} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Table */}
      {rows.length > 0 ? (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="overflow-x-auto max-h-[480px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Task", "Location", "Valid Time", "Lead Time", "Forecast", "Actual", "Error", "Model"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r: any) => (
                  <tr key={r.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}
                      className="transition-colors"
                      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                    <td className="px-4 py-2 font-medium" style={{ color: "var(--foreground)" }}>{r.task?.replace(/_/g, " ")}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{r.location_id}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{new Date(r.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{r.lead_time_hours}h</td>
                    <td className="px-4 py-2 font-semibold" style={{ color: "var(--chart-blue)" }}>{r.forecast_value?.toFixed(2) ?? "—"}</td>
                    <td className="px-4 py-2 font-semibold" style={{ color: "var(--chart-emerald)" }}>{r.actual_value?.toFixed(2) ?? "—"}</td>
                    <td className="px-4 py-2" style={{ color: r.error != null && Math.abs(r.error) > 2 ? "var(--danger)" : "var(--muted-foreground)" }}>
                      {r.error?.toFixed(3) ?? "—"}
                    </td>
                    <td className="px-4 py-2 font-mono text-[10px]" style={{ color: "var(--muted-foreground)" }}>{r.model_version_id?.slice(0, 16)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Pagination */}
          <div className="flex items-center justify-between px-5 py-3 border-t" style={{ borderColor: "var(--border)" }}>
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              Showing {page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total}
            </p>
            <div className="flex gap-1">
              <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}
                className="p-1.5 rounded-md border disabled:opacity-30" style={{ borderColor: "var(--border)" }}>
                <ChevronLeft size={14} />
              </button>
              <button onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}
                className="p-1.5 rounded-md border disabled:opacity-30" style={{ borderColor: "var(--border)" }}>
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <EmptyState title="No verification data" variant="data" />
      )}
    </div>
  );
}

function MC({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
      <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{label}</p>
      <p className="text-xl font-bold mt-1" style={{ color }}>{value}</p>
    </div>
  );
}
