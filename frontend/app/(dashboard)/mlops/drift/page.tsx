"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge } from "@/components/common/status-badge";
import { Activity } from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, chartHeight } from "@/lib/chart-theme";

export default function DriftMonitoringPage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true); setError(null);
    try { setData(await apiClient<any>("/api/v1/monitoring/drift")); }
    catch (e: any) { setError(e.message || "Failed"); } finally { setIsLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const events = data?.events || data?.drift_events || (Array.isArray(data) ? data : []);

  const chartData = events.map((e: any) => ({
    feature: e.feature?.replace(/_/g, " ") || "unknown",
    psi: e.psi ?? 0,
    threshold: e.threshold ?? 0.25,
    detected: e.detected,
  }));

  const driftCount = events.filter((e: any) => e.detected).length;

  return (
    <div className="space-y-6">
      <PageHeader title="Drift Monitoring" description="Feature distribution shift detection (PSI / KS)" icon={<Activity size={20} />} onRefresh={fetchData} isLoading={isLoading} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MC label="Features Monitored" value={events.length.toString()} color="var(--primary)" />
        <MC label="Drift Detected" value={driftCount.toString()} color={driftCount > 0 ? "var(--danger)" : "var(--success)"} />
        <MC label="No Drift" value={(events.length - driftCount).toString()} color="var(--success)" />
        <MC label="Threshold" value="PSI ≤ 0.25" color="var(--muted-foreground)" />
      </div>

      {chartData.length > 0 && (
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>PSI by Feature</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <BarChart data={chartData} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="feature" tick={{ fontSize: 10, fill: "var(--chart-text)" }} angle={-20} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Bar dataKey="psi" name="PSI" radius={[4, 4, 0, 0]}>
                {chartData.map((entry: any, i: number) => (
                  <Cell key={i} fill={entry.detected ? "var(--danger)" : entry.psi > 0.15 ? "var(--warning)" : "var(--success)"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {events.length > 0 ? (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--muted)" }}>
                  {["Feature", "PSI", "KS Statistic", "P-Value", "Threshold", "Status", "Detected At"].map(h => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {events.map((e: any, i: number) => (
                  <tr key={i} style={{ borderBottom: "1px solid var(--border-subtle)" }}
                      className="transition-colors"
                      onMouseEnter={(ev) => (ev.currentTarget.style.background = "var(--card-hover)")}
                      onMouseLeave={(ev) => (ev.currentTarget.style.background = "transparent")}>
                    <td className="px-4 py-2 font-medium" style={{ color: "var(--foreground)" }}>{e.feature}</td>
                    <td className="px-4 py-2 font-semibold" style={{ color: e.detected ? "var(--danger)" : "var(--foreground)" }}>{e.psi?.toFixed(4) ?? "—"}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{e.ks_statistic?.toFixed(4) ?? "—"}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{e.p_value?.toFixed(4) ?? "—"}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{e.threshold?.toFixed(2) ?? "0.25"}</td>
                    <td className="px-4 py-2">
                      <StatusBadge variant={e.detected ? "critical" : "healthy"}>
                        {e.detected ? "Drift Detected" : "No Drift"}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{e.timestamp ? new Date(e.timestamp).toLocaleString("en-IN", { day:"2-digit", month:"short", hour:"2-digit" }) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : <EmptyState title="No drift events" variant="data" />}
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
