"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge, stageBadgeVariant } from "@/components/common/status-badge";
import { BarChart3, Filter } from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, CHART_PALETTE, chartHeight } from "@/lib/chart-theme";

export default function ModelPerformancePage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [taskFilter, setTaskFilter] = useState<string>("all");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const url = taskFilter !== "all" ? `/api/v1/ml/performance?task=${taskFilter}` : "/api/v1/ml/performance";
      const resp = await apiClient<any>(url);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load model performance");
    } finally {
      setIsLoading(false);
    }
  }, [taskFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load model performance" message={error} onRetry={fetchData} />;
  if (!data) return null;

  const models = data.models || [];
  const verifSummary = data.verification_summary || [];
  const tasks = ([...new Set(models.map((m: any) => m.task))] as string[]).sort();
  const champions = models.filter((m: any) => m.stage === "Champion");
  const challengers = models.filter((m: any) => m.stage === "Challenger");

  // Chart: MAE by task (champions only)
  const maeByTask = tasks.map((task) => {
    const champ = champions.find((m: any) => m.task === task);
    const verif = verifSummary.find((v: any) => v.task === task);
    return {
      task: task.replace(/_/g, " "),
      "Champion MAE": champ?.mae ?? null,
      "Verification MAE": verif?.mae ?? null,
    };
  }).filter((d: any) => d["Champion MAE"] != null || d["Verification MAE"] != null);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Model Performance"
        description={`${models.length} model versions · ${champions.length} champions · ${challengers.length} challengers`}
        icon={<BarChart3 size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <div className="flex items-center gap-2">
          <Filter size={14} style={{ color: "var(--muted-foreground)" }} />
          <select
            value={taskFilter}
            onChange={(e) => setTaskFilter(e.target.value)}
            className="text-xs rounded-lg border px-3 py-1.5 font-medium"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <option value="all">All Tasks</option>
            {tasks.map((t) => (
              <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
            ))}
          </select>
        </div>
      </PageHeader>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Total Models" value={models.length.toString()} color="var(--primary)" />
        <MetricCard label="Champions" value={champions.length.toString()} color="var(--success)" />
        <MetricCard label="Challengers" value={challengers.length.toString()} color="var(--warning)" />
        <MetricCard label="Tasks Covered" value={tasks.length.toString()} color="var(--chart-violet)" />
      </div>

      {/* MAE Comparison Chart */}
      {maeByTask.length > 0 && (
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>MAE by Task (Champion Models)</h3>
          <ResponsiveContainer width="100%" height={chartHeight("md")}>
            <BarChart data={maeByTask} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
              <XAxis dataKey="task" tick={{ fontSize: 10, fill: "var(--chart-text)" }} angle={-25} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Bar dataKey="Champion MAE" fill={CHART_PALETTE[0]} radius={[4, 4, 0, 0]} barSize={20} />
              <Bar dataKey="Verification MAE" fill={CHART_PALETTE[1]} radius={[4, 4, 0, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Models Table */}
      <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="px-5 py-3 border-b" style={{ borderColor: "var(--border)" }}>
          <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>All Model Versions</h3>
        </div>
        <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
          <table className="w-full text-xs">
            <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
              <tr style={{ borderBottom: "1px solid var(--border)" }}>
                {["Model", "Task", "Horizon", "Stage", "MAE", "RMSE", "R²", "F1", "MASE", "Created"].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {models.map((m: any) => (
                <tr key={m.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}
                    className="transition-colors"
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                  <td className="px-4 py-2 font-medium" style={{ color: "var(--foreground)" }}>{m.model_name}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.task.replace(/_/g, " ")}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.horizon_hours}h</td>
                  <td className="px-4 py-2"><StatusBadge variant={stageBadgeVariant(m.stage)}>{m.stage}</StatusBadge></td>
                  <td className="px-4 py-2" style={{ color: "var(--foreground)" }}>{m.mae?.toFixed(4) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.rmse?.toFixed(4) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.r2?.toFixed(4) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.f1?.toFixed(4) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.mase?.toFixed(4) ?? "—"}</td>
                  <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{new Date(m.created_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Verification Summary */}
      {verifSummary.length > 0 && (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="px-5 py-3 border-b" style={{ borderColor: "var(--border)" }}>
            <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>Verification Summary by Task</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--muted)" }}>
                  {["Task", "Verified Forecasts", "MAE"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {verifSummary.map((v: any) => (
                  <tr key={v.task} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td className="px-4 py-2 font-medium" style={{ color: "var(--foreground)" }}>{v.task.replace(/_/g, " ")}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{v.count}</td>
                    <td className="px-4 py-2 font-semibold" style={{ color: "var(--chart-emerald)" }}>{v.mae?.toFixed(4) ?? "—"}</td>
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

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
      <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{label}</p>
      <p className="text-xl font-bold mt-1" style={{ color }}>{value}</p>
    </div>
  );
}
