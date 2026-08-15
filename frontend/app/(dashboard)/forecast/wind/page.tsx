"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge, stageBadgeVariant } from "@/components/common/status-badge";
import { Wind, Cpu } from "lucide-react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, ComposedChart, Bar, BarChart,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, SERIES_COLORS, chartHeight } from "@/lib/chart-theme";

export default function WindForecastPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/forecast/wind/${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load wind forecast");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load AI wind forecast" message={error} onRetry={fetchData} />;
  if (!data) return <EmptyState title="No wind predictions" variant="predictions" />;

  const champions = data.champions || {};
  const predictions = data.predictions || {};
  const speedPreds = predictions.wind_speed || [];
  const gustPreds = predictions.wind_gusts || [];
  const dirPreds = predictions.wind_direction || [];

  const speedChart = [...speedPreds]
    .sort((a: any, b: any) => new Date(a.valid_time).getTime() - new Date(b.valid_time).getTime())
    .map((p: any) => ({
      time: new Date(p.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit" }),
      speed: p.prediction,
    }));

  const gustChart = [...gustPreds]
    .sort((a: any, b: any) => new Date(a.valid_time).getTime() - new Date(b.valid_time).getTime())
    .map((p: any) => ({
      time: new Date(p.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit" }),
      gusts: p.prediction,
    }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Wind Forecast"
        description={`Wind speed, gusts & direction predictions · ${currentLocation?.name || locationId}`}
        icon={<Wind size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <StatusBadge variant="champion" dot>AI Prediction</StatusBadge>
      </PageHeader>

      {/* Champion Models */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {["wind_speed", "wind_gusts", "wind_direction"].map((task) => {
          const ch = champions[task];
          return (
            <div key={task} className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
                  {task.replace(/_/g, " ")}
                </h3>
                {ch && <StatusBadge variant="champion" dot={false}>Champion</StatusBadge>}
              </div>
              {ch ? (
                <div className="space-y-1">
                  <p className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{ch.model}</p>
                  <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>{ch.version}</p>
                  {ch.metrics?.mae != null && (
                    <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>MAE: <span className="font-semibold" style={{ color: "var(--foreground)" }}>{ch.metrics.mae.toFixed(3)}</span></p>
                  )}
                </div>
              ) : (
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>No champion model</p>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <MetricCard label="Speed Predictions" value={speedPreds.length.toString()} color="var(--chart-teal)" />
        <MetricCard label="Gust Predictions" value={gustPreds.length.toString()} color="var(--chart-orange)" />
        <MetricCard label="Direction Predictions" value={dirPreds.length.toString()} color="var(--chart-violet)" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {speedChart.length > 0 && (
          <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Wind Speed Prediction (km/h)</h3>
            <ResponsiveContainer width="100%" height={chartHeight("md")}>
              <AreaChart data={speedChart} margin={CHART_MARGIN}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--chart-text)" }} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit=" km/h" />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Area type="monotone" dataKey="speed" stroke={SERIES_COLORS.wind} fill={SERIES_COLORS.wind} fillOpacity={0.1} name="Wind Speed" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
        {gustChart.length > 0 && (
          <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Wind Gust Prediction (km/h)</h3>
            <ResponsiveContainer width="100%" height={chartHeight("md")}>
              <BarChart data={gustChart} margin={CHART_MARGIN}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--chart-text)" }} interval="preserveStartEnd" />
                <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit=" km/h" />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Bar dataKey="gusts" fill="var(--chart-orange)" name="Wind Gusts" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
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
