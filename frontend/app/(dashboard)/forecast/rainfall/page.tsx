"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge, stageBadgeVariant } from "@/components/common/status-badge";
import { CloudRain, Cpu } from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ComposedChart, Line,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, SERIES_COLORS, chartHeight } from "@/lib/chart-theme";

export default function RainfallForecastPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/forecast/rainfall/${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load rainfall forecast");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load AI rainfall forecast" message={error} onRetry={fetchData} />;
  if (!data) return <EmptyState title="No predictions" variant="predictions" />;

  const occChamp = data.occurrence_champion;
  const amtChamp = data.amount_champion;
  const occPreds = data.occurrence_predictions || [];
  const amtPreds = data.amount_predictions || [];

  const occChart = [...occPreds]
    .sort((a: any, b: any) => new Date(a.valid_time).getTime() - new Date(b.valid_time).getTime())
    .map((p: any) => ({
      time: new Date(p.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit" }),
      probability: p.rain_probability != null ? (p.rain_probability * 100) : (p.prediction != null ? p.prediction * 100 : null),
      horizon: p.horizon_hours,
    }));

  const amtChart = [...amtPreds]
    .sort((a: any, b: any) => new Date(a.valid_time).getTime() - new Date(b.valid_time).getTime())
    .map((p: any) => ({
      time: new Date(p.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit" }),
      amount: p.prediction,
      lower: p.p10 ?? p.lower,
      upper: p.p90 ?? p.upper,
    }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Rainfall Forecast"
        description={`Rain occurrence + precipitation amount · ${currentLocation?.name || locationId}`}
        icon={<CloudRain size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <StatusBadge variant="champion" dot>AI Prediction</StatusBadge>
      </PageHeader>

      {/* Champion Models */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {occChamp && (
          <ChampionCard
            title="Rain Occurrence (Classification)"
            model={occChamp.model}
            version={occChamp.version}
            metrics={occChamp.metrics}
          />
        )}
        {amtChamp && (
          <ChampionCard
            title="Precipitation Amount (Regression)"
            model={amtChamp.model}
            version={amtChamp.version}
            metrics={amtChamp.metrics}
          />
        )}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Occurrence Predictions" value={occPreds.length.toString()} color="var(--chart-cyan)" />
        <MetricCard label="Amount Predictions" value={amtPreds.length.toString()} color="var(--chart-blue)" />
        <MetricCard label="Occurrence F1" value={occChamp?.metrics?.f1 != null ? occChamp.metrics.f1.toFixed(3) : "—"} color="var(--chart-emerald)" />
        <MetricCard label="Amount MAE" value={amtChamp?.metrics?.mae != null ? `${amtChamp.metrics.mae.toFixed(3)} mm` : "—"} color="var(--chart-amber)" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {occChart.length > 0 && (
          <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Rain Probability (%)</h3>
            <ResponsiveContainer width="100%" height={chartHeight("md")}>
              <BarChart data={occChart} margin={CHART_MARGIN}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--chart-text)" }} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="%" domain={[0, 100]} />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Bar dataKey="probability" fill={SERIES_COLORS.rainProbability} name="Rain Probability (%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {amtChart.length > 0 && (
          <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Precipitation Amount (mm)</h3>
            <ResponsiveContainer width="100%" height={chartHeight("md")}>
              <ComposedChart data={amtChart} margin={CHART_MARGIN}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--chart-text)" }} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="mm" />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Legend wrapperStyle={{ fontSize: "11px" }} />
                <Bar dataKey="amount" fill={SERIES_COLORS.rainfall} name="Predicted (mm)" radius={[4, 4, 0, 0]} />
                <Line type="monotone" dataKey="upper" stroke="var(--chart-rose)" strokeDasharray="4 4" name="Upper (p90)" dot={false} />
                <Line type="monotone" dataKey="lower" stroke="var(--chart-blue)" strokeDasharray="4 4" name="Lower (p10)" dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Predictions Tables */}
      {occPreds.length > 0 && (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="px-5 py-3 border-b" style={{ borderColor: "var(--border)" }}>
            <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>Rain Occurrence Predictions</h3>
          </div>
          <div className="overflow-x-auto max-h-[320px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Valid Time", "Horizon", "Probability", "Rain Expected"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {occPreds.map((p: any) => {
                  const prob = p.rain_probability ?? p.prediction;
                  const pctStr = prob != null ? `${(prob * 100).toFixed(1)}%` : "—";
                  return (
                    <tr key={p.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                      <td className="px-4 py-2" style={{ color: "var(--foreground)" }}>{new Date(p.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</td>
                      <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{p.horizon_hours}h</td>
                      <td className="px-4 py-2 font-semibold" style={{ color: "var(--chart-cyan)" }}>{pctStr}</td>
                      <td className="px-4 py-2">
                        <StatusBadge variant={prob != null && prob > 0.5 ? "warning" : "healthy"} dot={false}>
                          {prob != null && prob > 0.5 ? "Yes" : "No"}
                        </StatusBadge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function ChampionCard({ title, model, version, metrics }: { title: string; model: string; version: string; metrics: any }) {
  return (
    <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2 rounded-lg" style={{ background: "var(--success-muted)" }}>
          <Cpu size={16} style={{ color: "var(--success)" }} />
        </div>
        <div>
          <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{title}</h3>
          <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>{model} · {version}</p>
        </div>
        <StatusBadge variant="champion" className="ml-auto">Champion</StatusBadge>
      </div>
      {metrics && (
        <div className="flex flex-wrap gap-3 text-xs" style={{ color: "var(--muted-foreground)" }}>
          {Object.entries(metrics).slice(0, 5).map(([k, v]) => (
            <span key={k}>{k}: <span className="font-semibold" style={{ color: "var(--foreground)" }}>{typeof v === "number" ? v.toFixed(4) : String(v)}</span></span>
          ))}
        </div>
      )}
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
