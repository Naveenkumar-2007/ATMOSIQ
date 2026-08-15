"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge, healthBadgeVariant } from "@/components/common/status-badge";
import { HeartPulse, Server, Database, Cpu, Activity, Zap } from "lucide-react";

const SERVICE_ICONS: Record<string, React.ReactNode> = {
  "Database": <Database size={18} />,
  "API": <Server size={18} />,
  "ML Models": <Cpu size={18} />,
  "Data Ingestion": <Activity size={18} />,
  "Prediction Service": <Zap size={18} />,
  "Monitoring": <HeartPulse size={18} />,
};

export default function SystemHealthPage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true); setError(null);
    try { setData(await apiClient<any>("/api/v1/system/health")); }
    catch (e: any) { setError(e.message || "Failed"); } finally { setIsLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;
  if (!data) return null;

  const services = data.services || [];

  return (
    <div className="space-y-6">
      <PageHeader title="System Health" description={`AtmosIQ v${data.version}`} icon={<HeartPulse size={20} />} onRefresh={fetchData} isLoading={isLoading}>
        <StatusBadge variant={healthBadgeVariant(data.status)}>{data.status?.toUpperCase()}</StatusBadge>
      </PageHeader>

      {/* Overall Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MC label="Models" value={data.model_count?.toLocaleString() || "0"} color="var(--primary)" />
        <MC label="Champions" value={data.champion_count?.toString() || "0"} color="var(--success)" />
        <MC label="Observations" value={data.observation_count?.toLocaleString() || "0"} color="var(--chart-blue)" />
        <MC label="Predictions" value={data.prediction_count?.toLocaleString() || "0"} color="var(--chart-violet)" />
      </div>

      {/* Timestamps */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: "Last Ingestion", value: data.last_ingestion },
          { label: "Last Prediction", value: data.last_prediction },
          { label: "Last Training", value: data.last_training },
        ].map((t) => (
          <div key={t.label} className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{t.label}</p>
            <p className="text-sm font-semibold mt-1" style={{ color: "var(--foreground)" }}>
              {t.value ? new Date(t.value).toLocaleString("en-IN") : "Never"}
            </p>
          </div>
        ))}
      </div>

      {/* Services */}
      <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>Service Status</h3>
        <div className="space-y-3">
          {services.map((svc: any) => (
            <div key={svc.name} className="flex items-center justify-between py-3 border-b last:border-0" style={{ borderColor: "var(--border-subtle)" }}>
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg" style={{ background: svc.status === "healthy" ? "var(--success-muted)" : svc.status === "degraded" ? "var(--warning-muted)" : "var(--danger-muted)" }}>
                  <span style={{ color: svc.status === "healthy" ? "var(--success)" : svc.status === "degraded" ? "var(--warning)" : "var(--danger)" }}>
                    {SERVICE_ICONS[svc.name] || <Server size={18} />}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium" style={{ color: "var(--foreground)" }}>{svc.name}</p>
                  {svc.details && <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>{svc.details}</p>}
                </div>
              </div>
              <div className="flex items-center gap-3">
                {svc.latency_ms != null && (
                  <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>{svc.latency_ms.toFixed(0)}ms</span>
                )}
                <StatusBadge variant={healthBadgeVariant(svc.status)}>{svc.status}</StatusBadge>
              </div>
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
