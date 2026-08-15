"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge, stageBadgeVariant } from "@/components/common/status-badge";
import { Thermometer, TrendingUp, Cpu } from "lucide-react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, SERIES_COLORS, chartHeight } from "@/lib/chart-theme";

export default function TemperatureForecastPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/forecast/temperature/${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load temperature forecast");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load AI temperature forecast" message={error} onRetry={fetchData} />;
  if (!data) return <EmptyState title="No predictions" message="No ML temperature predictions found. Run inference first." variant="predictions" />;

  const champion = data.champion;
  const predictions = data.predictions || [];
  const summary = data.verification_summary || {};

  // Prepare chart data from predictions (sorted by valid_time ascending)
  const chartData = [...predictions]
    .sort((a: any, b: any) => new Date(a.valid_time).getTime() - new Date(b.valid_time).getTime())
    .map((p: any) => ({
      time: new Date(p.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }),
      prediction: p.prediction,
      lower: p.lower,
      upper: p.upper,
    }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Temperature Forecast"
        description={`ML-powered temperature prediction · ${currentLocation?.name || locationId}`}
        icon={<Thermometer size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <StatusBadge variant="champion" dot>AI Prediction</StatusBadge>
      </PageHeader>

      {/* Champion Model Info */}
      {champion && (
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl" style={{ background: "var(--success-muted)" }}>
                <Cpu size={18} style={{ color: "var(--success)" }} />
              </div>
              <div>
                <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Champion Model: {champion.model}</h3>
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>Version: {champion.version}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <StatusBadge variant={stageBadgeVariant(champion.stage)}>{champion.stage}</StatusBadge>
              {champion.metrics && (
                <div className="flex gap-4 text-xs">
                  {champion.metrics.mae != null && (
                    <span style={{ color: "var(--muted-foreground)" }}>MAE: <span className="font-semibold" style={{ color: "var(--foreground)" }}>{champion.metrics.mae.toFixed(3)}°C</span></span>
                  )}
                  {champion.metrics.rmse != null && (
                    <span style={{ color: "var(--muted-foreground)" }}>RMSE: <span className="font-semibold" style={{ color: "var(--foreground)" }}>{champion.metrics.rmse.toFixed(3)}°C</span></span>
                  )}
                  {champion.metrics.r2 != null && (
                    <span style={{ color: "var(--muted-foreground)" }}>R²: <span className="font-semibold" style={{ color: "var(--foreground)" }}>{champion.metrics.r2.toFixed(4)}</span></span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Predictions" value={predictions.length.toString()} color="var(--primary)" />
        <MetricCard label="Verified MAE" value={summary.mae != null ? `${summary.mae.toFixed(2)}°C` : "—"} color="var(--chart-emerald)" />
        <MetricCard label="Verified RMSE" value={summary.rmse != null ? `${summary.rmse.toFixed(2)}°C` : "—"} color="var(--chart-amber)" />
        <MetricCard label="Verified Bias" value={summary.bias != null ? `${summary.bias > 0 ? "+" : ""}${summary.bias.toFixed(2)}°C` : "—"} color="var(--chart-violet)" />
      </div>

      {/* Prediction Chart with Uncertainty */}
      {chartData.length > 0 && (
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Temperature Prediction with Uncertainty Interval</h3>
          <ResponsiveContainer width="100%" height={chartHeight("lg")}>
            <AreaChart data={chartData} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--chart-text)" }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="°C" />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Area type="monotone" dataKey="upper" stroke="none" fill={SERIES_COLORS.uncertainty} fillOpacity={0.2} name="Upper Bound (p90)" />
              <Area type="monotone" dataKey="lower" stroke="none" fill={SERIES_COLORS.uncertainty} fillOpacity={0.2} name="Lower Bound (p10)" />
              <Line type="monotone" dataKey="prediction" stroke={SERIES_COLORS.forecast} name="Prediction (°C)" strokeWidth={2} dot={{ r: 3 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Predictions Table */}
      <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="px-5 py-3 border-b" style={{ borderColor: "var(--border)" }}>
          <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>Recent Predictions</h3>
        </div>
        <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                {["Issue Time", "Valid Time", "Horizon", "Prediction", "Lower (p10)", "Upper (p90)", "Model"].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {predictions.map((p: any) => (
                <tr key={p.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}
                    className="transition-colors"
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{new Date(p.issue_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</td>
                  <td className="px-4 py-2" style={{ color: "var(--foreground)" }}>{new Date(p.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{p.horizon_hours}h</td>
                  <td className="px-4 py-2 font-semibold" style={{ color: "var(--foreground)" }}>{p.prediction?.toFixed(2) ?? "—"}°C</td>
                  <td className="px-4 py-2" style={{ color: "var(--chart-blue)" }}>{p.lower?.toFixed(2) ?? "—"}°C</td>
                  <td className="px-4 py-2" style={{ color: "var(--chart-rose)" }}>{p.upper?.toFixed(2) ?? "—"}°C</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{p.model || p.model_version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
      <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{label}</p>
      <p className="text-xl font-bold mt-1" style={{ color }}>{value}</p>
    </div>
  );
}
