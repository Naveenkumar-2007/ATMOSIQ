"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge } from "@/components/common/status-badge";
import { Gauge } from "lucide-react";

export default function ModelMonitoringPage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true); setError(null);
    try { setData(await apiClient<any>("/api/v1/mlops/model-monitoring")); }
    catch (e: any) { setError(e.message || "Failed"); } finally { setIsLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <PageHeader title="Model Monitoring" description="Production ML model health and telemetry" icon={<Gauge size={20} />} onRefresh={fetchData} isLoading={isLoading}>
        <StatusBadge variant={data.error_rate > 0.05 ? "critical" : "healthy"}>
          {data.error_rate > 0.05 ? "Degraded" : "All Systems Operational"}
        </StatusBadge>
      </PageHeader>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MC label="Predictions (24h)" value={data.prediction_volume_24h?.toLocaleString() || "0"} color="var(--primary)" />
        <MC label="Predictions (7d)" value={data.prediction_volume_7d?.toLocaleString() || "0"} color="var(--chart-blue)" />
        <MC label="Active Models" value={data.active_models?.toString() || "0"} color="var(--chart-emerald)" />
        <MC label="Champions" value={data.champion_models?.toString() || "0"} color="var(--success)" />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MC label="Avg Latency" value={data.avg_latency_ms != null ? `${data.avg_latency_ms.toFixed(1)} ms` : "N/A"} color="var(--chart-amber)" />
        <MC label="Error Rate" value={`${(data.error_rate * 100).toFixed(2)}%`} color={data.error_rate > 0.01 ? "var(--danger)" : "var(--success)"} />
        <MC label="Drift Events (30d)" value={data.drift_events_30d?.toString() || "0"} color={data.drift_events_30d > 0 ? "var(--warning)" : "var(--success)"} />
        <MC label="Perf Events (30d)" value={data.performance_events_30d?.toString() || "0"} color={data.performance_events_30d > 0 ? "var(--warning)" : "var(--success)"} />
      </div>

      {/* Operational Status */}
      <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Operational Status</h3>
        <div className="space-y-3">
          {[
            { name: "Prediction Pipeline", status: data.error_rate < 0.01 ? "healthy" : "degraded", detail: `${data.prediction_volume_24h} predictions in last 24h` },
            { name: "Model Registry", status: data.champion_models > 0 ? "healthy" : "warning", detail: `${data.champion_models} champion models active` },
            { name: "Drift Detection", status: data.drift_events_30d === 0 ? "healthy" : "warning", detail: `${data.drift_events_30d} drift events in 30 days` },
            { name: "Performance Monitoring", status: data.performance_events_30d === 0 ? "healthy" : "warning", detail: `${data.performance_events_30d} performance events in 30 days` },
          ].map((svc) => (
            <div key={svc.name} className="flex items-center justify-between py-2 border-b" style={{ borderColor: "var(--border-subtle)" }}>
              <div className="flex items-center gap-3">
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: svc.status === "healthy" ? "var(--success)" : svc.status === "warning" ? "var(--warning)" : "var(--danger)" }} />
                <span className="text-sm font-medium" style={{ color: "var(--foreground)" }}>{svc.name}</span>
              </div>
              <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>{svc.detail}</span>
            </div>
          ))}
        </div>
      </div>
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
