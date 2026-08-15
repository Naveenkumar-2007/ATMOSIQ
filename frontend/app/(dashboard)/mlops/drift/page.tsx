"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge } from "@/components/common/status-badge";
import { Activity, ShieldCheck, AlertTriangle, CheckCircle2 } from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, Legend
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN } from "@/lib/chart-theme";

export default function DriftMonitoringPage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/monitoring/summary`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load drift data");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load drift monitoring" message={error} onRetry={fetchData} />;

  // Drift Score Timeline matching Card 12
  const driftTimeline = [
    { date: "18 Jul", score: 0.18 },
    { date: "22 Jul", score: 0.22 },
    { date: "26 Jul", score: 0.35 },
    { date: "29 Jul", score: 0.14 },
    { date: "3 Aug",  score: 0.42 },
    { date: "9 Aug",  score: 0.28 },
    { date: "15 Aug", score: 0.19 },
  ];

  const topDriftingFeatures = [
    { feature: "humidity", psi: 0.58, status: "Warning", color: "var(--chart-amber)" },
    { feature: "wind_speed", psi: 0.52, status: "Warning", color: "var(--chart-amber)" },
    { feature: "pressure", psi: 0.23, status: "No Drift", color: "var(--success)" },
    { feature: "temperature", psi: 0.16, status: "No Drift", color: "var(--success)" },
    { feature: "visibility", psi: 0.12, status: "No Drift", color: "var(--success)" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Drift Monitoring"
        description="Detecting covariate drift and statistical shifts in atmospheric feature distributions"
        icon={<Activity size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <StatusBadge variant="healthy" dot>Population Stability Index (PSI)</StatusBadge>
      </PageHeader>

      {/* 4 Drift Status Cards (Matching Card 12 in Reference Image) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Drift Status</span>
          <p className="text-xl font-extrabold" style={{ color: "var(--success)" }}>No Significant Drift</p>
          <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>All systems operating within bounds</p>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Features Monitored</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>24</p>
          <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Primary atmospheric signals</p>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Features with Drift</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--chart-amber)" }}>2</p>
          <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Mild seasonal variation</p>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Last Alert</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>2 days ago</p>
          <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Automated alert resolved</p>
        </div>
      </div>

      {/* Main Grid: Drift Timeline + Top Drifting Features (Matching Card 12) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Drift Score Timeline Chart */}
        <div className="lg:col-span-2 rounded-2xl border p-6" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
            <div>
              <h3 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                Drift Score Timeline
              </h3>
              <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
                Kolmogorov-Smirnov / PSI metric trajectory
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs font-semibold">
              <span className="flex items-center gap-1.5" style={{ color: "var(--success)" }}>
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--success)" }} />
                No Drift (&lt;0.3)
              </span>
              <span className="flex items-center gap-1.5" style={{ color: "var(--chart-amber)" }}>
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--chart-amber)" }} />
                Warning (0.3–0.5)
              </span>
              <span className="flex items-center gap-1.5" style={{ color: "var(--chart-rose)" }}>
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--chart-rose)" }} />
                Drift (&gt;0.5)
              </span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={driftTimeline} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--chart-text)" }} axisLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} domain={[0, 0.8]} axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <ReferenceLine y={0.3} stroke="var(--chart-amber)" strokeDasharray="4 4" label={{ value: "Warning (0.3)", fill: "var(--chart-amber)", fontSize: 10 }} />
              <ReferenceLine y={0.5} stroke="var(--chart-rose)" strokeDasharray="4 4" label={{ value: "Critical Drift (0.5)", fill: "var(--chart-rose)", fontSize: 10 }} />
              <Line type="monotone" dataKey="score" stroke="var(--chart-teal)" strokeWidth={3} dot={{ r: 5, fill: "var(--chart-teal)" }} name="Drift Score" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Right Col: Top Drifting Features */}
        <div className="rounded-2xl border p-6 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: "var(--muted-foreground)" }}>
              Top Drifting Features
            </h4>
            <div className="space-y-2.5">
              {topDriftingFeatures.map((f, idx) => (
                <div key={f.feature} className="flex items-center justify-between p-3 rounded-xl text-xs" style={{ background: "var(--muted)" }}>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[11px] font-bold" style={{ color: "var(--muted-foreground)" }}>{idx + 1}.</span>
                    <span className="font-semibold" style={{ color: "var(--foreground)" }}>{f.feature}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold" style={{ color: f.color }}>{f.psi.toFixed(2)}</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full"
                          style={{
                            background: f.status === "Warning" ? "rgba(245, 158, 11, 0.15)" : "rgba(16, 185, 129, 0.15)",
                            color: f.color
                          }}>
                      [{f.status}]
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => window.location.href = "/mlops/alerts"}
            className="w-full mt-4 py-2.5 rounded-xl font-bold text-xs transition-all"
            style={{ background: "var(--muted)", color: "var(--foreground)", border: "1px solid var(--border)" }}
          >
            View All Features
          </button>
        </div>
      </div>
    </div>
  );
}
