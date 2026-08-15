"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge, stageBadgeVariant } from "@/components/common/status-badge";
import { GraduationCap } from "lucide-react";

export default function TrainingRunsPage() {
  const [runs, setRuns] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true); setError(null);
    try {
      const resp = await apiClient<any>("/api/v1/mlops/training-runs");
      setRuns(Array.isArray(resp) ? resp : resp?.runs || []);
    } catch (e: any) { setError(e.message || "Failed"); } finally { setIsLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="space-y-6">
      <PageHeader title="Training Runs" description={`${runs.length} training runs recorded`} icon={<GraduationCap size={20} />} onRefresh={fetchData} isLoading={isLoading} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MC label="Total Runs" value={runs.length.toString()} color="var(--primary)" />
        <MC label="Unique Models" value={[...new Set(runs.map((r: any) => r.model_name))].length.toString()} color="var(--chart-violet)" />
        <MC label="Unique Tasks" value={[...new Set(runs.map((r: any) => r.task))].length.toString()} color="var(--chart-emerald)" />
        <MC label="Avg Duration" value={runs.length > 0 ? `${(runs.reduce((a: number, r: any) => a + (r.duration_seconds || 0), 0) / runs.length).toFixed(1)}s` : "—"} color="var(--chart-amber)" />
      </div>

      {runs.length > 0 ? (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Run ID", "Model", "Task", "Horizon", "MAE", "RMSE", "R²", "F1", "Duration", "Created"].map(h => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {runs.map((r: any) => {
                  const m = r.metrics || {};
                  return (
                    <tr key={r.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}
                        className="transition-colors"
                        onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                        onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                      <td className="px-4 py-2 font-mono text-[10px]" style={{ color: "var(--muted-foreground)" }}>{r.id?.slice(0,16)}</td>
                      <td className="px-4 py-2 font-medium" style={{ color: "var(--foreground)" }}>{r.model_name}</td>
                      <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{(r.task || "").replace(/_/g," ")}</td>
                      <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{r.horizon_hours}h</td>
                      <td className="px-4 py-2" style={{ color: "var(--foreground)" }}>{m.mae?.toFixed(4) ?? "—"}</td>
                      <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.rmse?.toFixed(4) ?? "—"}</td>
                      <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.r2?.toFixed(4) ?? "—"}</td>
                      <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.f1?.toFixed(4) ?? m.tuned_f1?.toFixed(4) ?? "—"}</td>
                      <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{r.duration_seconds?.toFixed(1) ?? "—"}s</td>
                      <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{r.created_at ? new Date(r.created_at).toLocaleString("en-IN", { day:"2-digit", month:"short", hour:"2-digit" }) : "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : <EmptyState title="No training runs" variant="data" />}
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
