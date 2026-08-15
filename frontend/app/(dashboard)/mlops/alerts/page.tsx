"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge, severityBadgeVariant } from "@/components/common/status-badge";
import { Bell, CheckCircle2, XCircle } from "lucide-react";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("all");

  const fetchData = useCallback(async () => {
    setIsLoading(true); setError(null);
    try {
      const resp = await apiClient<any[]>("/api/v1/alerts");
      setAlerts(Array.isArray(resp) ? resp : []);
    } catch (e: any) { setError(e.message || "Failed"); } finally { setIsLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleAcknowledge = async (id: string) => {
    try {
      await apiClient(`/api/v1/alerts/${id}/acknowledge`, { method: "POST" });
      fetchData();
    } catch {}
  };

  const handleResolve = async (id: string) => {
    try {
      await apiClient(`/api/v1/alerts/${id}/resolve`, { method: "POST" });
      fetchData();
    } catch {}
  };

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const filtered = filter === "all" ? alerts : alerts.filter(a => a.status === filter);
  const active = alerts.filter(a => a.status === "active").length;
  const critical = alerts.filter(a => a.severity === "critical").length;

  return (
    <div className="space-y-6">
      <PageHeader title="Alerts" description={`${alerts.length} total · ${active} active · ${critical} critical`} icon={<Bell size={20} />} onRefresh={fetchData} isLoading={isLoading}>
        <select value={filter} onChange={(e) => setFilter(e.target.value)}
          className="text-xs rounded-lg border px-3 py-1.5 font-medium"
          style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}>
          <option value="all">All</option>
          <option value="active">Active</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
        </select>
      </PageHeader>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MC label="Total Alerts" value={alerts.length.toString()} color="var(--primary)" />
        <MC label="Active" value={active.toString()} color={active > 0 ? "var(--warning)" : "var(--success)"} />
        <MC label="Critical" value={critical.toString()} color={critical > 0 ? "var(--danger)" : "var(--success)"} />
        <MC label="Resolved" value={alerts.filter(a => a.status === "resolved").length.toString()} color="var(--success)" />
      </div>

      {filtered.length > 0 ? (
        <div className="space-y-3">
          {filtered.map((a: any) => (
            <div key={a.id} className="rounded-xl border p-4 transition-all" style={{ background: "var(--card)", borderColor: a.severity === "critical" ? "var(--danger)" : "var(--card-border)" }}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <StatusBadge variant={severityBadgeVariant(a.severity)}>{a.severity}</StatusBadge>
                    <StatusBadge variant={a.status === "active" ? "warning" : a.status === "resolved" ? "healthy" : "info"} dot={false}>{a.status}</StatusBadge>
                    <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>{a.alert_type || a.type}</span>
                  </div>
                  <p className="text-sm font-medium" style={{ color: "var(--foreground)" }}>{a.message}</p>
                  {a.recommendation && <p className="text-xs mt-1" style={{ color: "var(--muted-foreground)" }}>{a.recommendation}</p>}
                  <p className="text-[10px] mt-2" style={{ color: "var(--muted-foreground)" }}>
                    {a.created_at ? new Date(a.created_at).toLocaleString("en-IN") : ""} · {a.location || a.scope || ""}
                  </p>
                </div>
                {a.status === "active" && (
                  <div className="flex gap-2 shrink-0">
                    <button onClick={() => handleAcknowledge(a.id)} className="px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors"
                      style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }} title="Acknowledge">
                      <CheckCircle2 size={14} />
                    </button>
                    <button onClick={() => handleResolve(a.id)} className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
                      style={{ background: "var(--success)", color: "var(--success-foreground)" }} title="Resolve">
                      <XCircle size={14} />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : <EmptyState title="No alerts" message="No alerts match the current filter." />}
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
