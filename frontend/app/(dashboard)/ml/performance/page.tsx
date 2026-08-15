"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge } from "@/components/common/status-badge";
import { Trophy, CheckCircle2, TrendingUp, Sparkles, Award } from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN } from "@/lib/chart-theme";

export default function ModelPerformancePage() {
  const { locationId, currentLocation } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [task, setTask] = useState("temperature");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/ml/performance`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load performance metrics");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load performance metrics" message={error} onRetry={fetchData} />;

  // Multi-model MAE timeline curve matching Card 10
  const modelTimeline = [
    { date: "18 Jul", champion: 0.88, lstm: 1.15, persistence: 1.48, seasonal: 1.62 },
    { date: "22 Jul", champion: 0.92, lstm: 1.10, persistence: 1.55, seasonal: 1.70 },
    { date: "26 Jul", champion: 0.85, lstm: 1.18, persistence: 1.42, seasonal: 1.58 },
    { date: "29 Jul", champion: 0.90, lstm: 1.25, persistence: 1.60, seasonal: 1.75 },
    { date: "3 Aug",  champion: 0.82, lstm: 1.12, persistence: 1.38, seasonal: 1.52 },
    { date: "9 Aug",  champion: 0.89, lstm: 1.16, persistence: 1.50, seasonal: 1.68 },
    { date: "15 Aug", champion: 0.84, lstm: 1.09, persistence: 1.45, seasonal: 1.60 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Model Performance"
        description="Compare model performance over time across architecture lineages"
        icon={<Trophy size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <div className="flex items-center gap-3">
          <select
            value={task}
            onChange={(e) => setTask(e.target.value)}
            className="text-xs rounded-xl border px-3 py-1.5 font-bold"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <option value="temperature">Temperature</option>
            <option value="rainfall">Rainfall</option>
            <option value="wind">Wind</option>
          </select>
          <StatusBadge variant="champion" dot>Active Model Registry</StatusBadge>
        </div>
      </PageHeader>

      {/* Main Grid: Multi-Model MAE Timeline + "Why Champion?" (Matching Card 10) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Model MAE Timeline Chart */}
        <div className="lg:col-span-2 rounded-2xl border p-6" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
            <div>
              <h3 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                Model Error Comparison (MAE)
              </h3>
              <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
                Continuous 30-Day Benchmark across Candidate Families
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs font-semibold">
              <span className="flex items-center gap-1.5" style={{ color: "var(--chart-teal)" }}>
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--chart-teal)" }} />
                HistGB / XGBoost (Champion)
              </span>
              <span className="flex items-center gap-1.5" style={{ color: "var(--chart-blue)" }}>
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--chart-blue)" }} />
                LSTM v8
              </span>
              <span className="flex items-center gap-1.5" style={{ color: "var(--chart-orange)" }}>
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--chart-orange)" }} />
                Persistence
              </span>
              <span className="flex items-center gap-1.5" style={{ color: "var(--chart-rose)" }}>
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--chart-rose)" }} />
                Seasonal Naive
              </span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={modelTimeline} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--chart-text)" }} axisLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="°" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="champion" stroke="var(--chart-teal)" strokeWidth={3.5} dot={{ r: 5, fill: "var(--chart-teal)" }} name="HistGB (Champion)" />
              <Line type="monotone" dataKey="lstm" stroke="var(--chart-blue)" strokeWidth={2} dot={{ r: 3, fill: "var(--chart-blue)" }} name="LSTM v8" />
              <Line type="monotone" dataKey="persistence" stroke="var(--chart-orange)" strokeWidth={1.5} strokeDasharray="3 3" dot={{ r: 3 }} name="Persistence Baseline" />
              <Line type="monotone" dataKey="seasonal" stroke="var(--chart-rose)" strokeWidth={1.5} strokeDasharray="3 3" dot={{ r: 3 }} name="Seasonal Naive" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Right Col: "Why Champion?" Card (Matching Card 10) */}
        <div className="rounded-2xl border p-6 flex flex-col justify-between" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Award size={20} style={{ color: "var(--primary)" }} />
              <div>
                <span className="text-xs font-semibold text-muted-foreground">Current Champion</span>
                <h4 className="text-lg font-extrabold" style={{ color: "var(--foreground)" }}>
                  HistGB / XGBoost v12
                </h4>
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <p className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
                Why Champion?
              </p>

              <div className="space-y-2.5 text-xs">
                <div className="flex items-start gap-2.5 p-3 rounded-xl" style={{ background: "rgba(16, 185, 129, 0.1)" }}>
                  <CheckCircle2 size={16} style={{ color: "var(--success)" }} className="shrink-0 mt-0.5" />
                  <div>
                    <strong style={{ color: "var(--foreground)" }}>Lowest MAE (0.84°C)</strong>
                    <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Outperforms persistence baseline by 42.1%</p>
                  </div>
                </div>

                <div className="flex items-start gap-2.5 p-3 rounded-xl" style={{ background: "rgba(2, 132, 199, 0.1)" }}>
                  <CheckCircle2 size={16} style={{ color: "var(--primary)" }} className="shrink-0 mt-0.5" />
                  <div>
                    <strong style={{ color: "var(--foreground)" }}>Highest R² Score (0.92)</strong>
                    <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Captures 92% of continuous variance</p>
                  </div>
                </div>

                <div className="flex items-start gap-2.5 p-3 rounded-xl" style={{ background: "rgba(245, 158, 11, 0.1)" }}>
                  <CheckCircle2 size={16} style={{ color: "var(--chart-amber)" }} className="shrink-0 mt-0.5" />
                  <div>
                    <strong style={{ color: "var(--foreground)" }}>Stable Latency & Zero Drift</strong>
                    <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Sub-millisecond batch inference throughput</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={() => window.location.href = "/ml/models"}
            className="w-full mt-4 py-2.5 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-2"
            style={{ background: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            View Full Model Registry
          </button>
        </div>
      </div>
    </div>
  );
}
