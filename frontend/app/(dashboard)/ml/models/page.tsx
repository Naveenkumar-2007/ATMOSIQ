"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge, stageBadgeVariant } from "@/components/common/status-badge";
import { Boxes, Filter } from "lucide-react";

export default function ModelsPage() {
  const [models, setModels] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stageFilter, setStageFilter] = useState("all");

  const fetchData = useCallback(async () => {
    setIsLoading(true); setError(null);
    try {
      const resp = await apiClient<any[]>("/api/v1/models");
      setModels(Array.isArray(resp) ? resp : []);
    } catch (e: any) { setError(e.message || "Failed"); } finally { setIsLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const filtered = stageFilter === "all" ? models : models.filter((m: any) => m.stage === stageFilter);
  const stages = [...new Set(models.map((m: any) => m.stage))];
  const champs = models.filter((m: any) => m.stage === "Champion").length;

  return (
    <div className="space-y-6">
      <PageHeader title="Model Registry" description={`${models.length} models · ${champs} champions`} icon={<Boxes size={20} />} onRefresh={fetchData} isLoading={isLoading}>
        <select value={stageFilter} onChange={(e) => setStageFilter(e.target.value)}
          className="text-xs rounded-lg border px-3 py-1.5 font-medium"
          style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}>
          <option value="all">All Stages</option>
          {stages.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </PageHeader>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stages.map(s => (
          <div key={s} className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{s}</p>
            <p className="text-2xl font-bold mt-1" style={{ color: s === "Champion" ? "var(--success)" : s === "Challenger" ? "var(--warning)" : "var(--muted-foreground)" }}>
              {models.filter((m: any) => m.stage === s).length}
            </p>
          </div>
        ))}
      </div>

      {filtered.length > 0 ? (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["ID", "Model", "Task", "Horizon", "Stage", "Location"].map(h => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((m: any) => (
                  <tr key={m.id} style={{ borderBottom: "1px solid var(--border-subtle)" }} className="transition-colors"
                      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                    <td className="px-4 py-2 font-mono text-[10px]" style={{ color: "var(--muted-foreground)" }}>{m.id?.slice(0,20)}</td>
                    <td className="px-4 py-2 font-medium" style={{ color: "var(--foreground)" }}>{m.model_name}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{(m.task || "").replace(/_/g," ")}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.horizon_hours}h</td>
                    <td className="px-4 py-2"><StatusBadge variant={stageBadgeVariant(m.stage)}>{m.stage}</StatusBadge></td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{m.location_id || "global"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : <EmptyState title="No models found" variant="data" />}
    </div>
  );
}
