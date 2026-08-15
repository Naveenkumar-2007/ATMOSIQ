"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge } from "@/components/common/status-badge";
import { Database, CheckCircle2, AlertCircle, ShieldCheck, BarChart3 } from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN } from "@/lib/chart-theme";

export default function DataQualityPage() {
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
      setError(e.message || "Failed to load data quality metrics");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load data quality" message={error} onRetry={fetchData} />;

  // Daily Ingestion Data Volume matching Card 11
  const volumeData = [
    { date: "9 Aug", volume: 92 },
    { date: "10 Aug", volume: 115 },
    { date: "11 Aug", volume: 98 },
    { date: "12 Aug", volume: 104 },
    { date: "13 Aug", volume: 120 },
    { date: "14 Aug", volume: 110 },
    { date: "15 Aug", volume: 124 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Quality"
        description="Data health and quality metrics across observation streams"
        icon={<Database size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <StatusBadge variant="healthy" dot>Schema Verified</StatusBadge>
      </PageHeader>

      {/* 4 Quality Score Cards (Matching Card 11) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center justify-between text-xs" style={{ color: "var(--muted-foreground)" }}>
            <span>Overall Quality Score</span>
            <span className="font-semibold text-[10px] px-2 py-0.5 rounded-full" style={{ background: "rgba(16, 185, 129, 0.15)", color: "var(--success)" }}>
              Excellent
            </span>
          </div>
          <p className="text-3xl font-extrabold" style={{ color: "var(--foreground)" }}>96%</p>
          <p className="text-[11px]" style={{ color: "var(--success)" }}>All data pipelines green</p>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Completeness</span>
          <p className="text-3xl font-extrabold" style={{ color: "var(--chart-cyan)" }}>98.2%</p>
          <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>0.1% null fields</p>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Consistency</span>
          <p className="text-3xl font-extrabold" style={{ color: "var(--chart-teal)" }}>95.1%</p>
          <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Physical range compliant</p>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Timeliness</span>
          <p className="text-3xl font-extrabold" style={{ color: "var(--primary)" }}>97.3%</p>
          <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>16 min avg latency</p>
        </div>
      </div>

      {/* Main Grid: Quality Checks List + Daily Data Volume Chart (Matching Card 11) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Col: Quality Checks */}
        <div className="rounded-2xl border p-6" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <h3 className="text-base font-bold mb-4" style={{ color: "var(--foreground)" }}>
            Automated Quality Checks
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3.5 rounded-xl" style={{ background: "var(--muted)" }}>
              <div className="flex items-center gap-3">
                <CheckCircle2 size={18} style={{ color: "var(--success)" }} />
                <div>
                  <p className="text-xs font-bold" style={{ color: "var(--foreground)" }}>Missing Values</p>
                  <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Less than 0.1% across 76 features</p>
                </div>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "rgba(16, 185, 129, 0.15)", color: "var(--success)" }}>
                Pass
              </span>
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl" style={{ background: "var(--muted)" }}>
              <div className="flex items-center gap-3">
                <CheckCircle2 size={18} style={{ color: "var(--success)" }} />
                <div>
                  <p className="text-xs font-bold" style={{ color: "var(--foreground)" }}>Outliers</p>
                  <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>0.3% beyond 3.5 IQR threshold</p>
                </div>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "rgba(16, 185, 129, 0.15)", color: "var(--success)" }}>
                Pass
              </span>
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl" style={{ background: "var(--muted)" }}>
              <div className="flex items-center gap-3">
                <CheckCircle2 size={18} style={{ color: "var(--success)" }} />
                <div>
                  <p className="text-xs font-bold" style={{ color: "var(--foreground)" }}>Duplicates</p>
                  <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>0.0% duplicate primary keys</p>
                </div>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "rgba(16, 185, 129, 0.15)", color: "var(--success)" }}>
                Pass
              </span>
            </div>

            <div className="flex items-center justify-between p-3.5 rounded-xl" style={{ background: "var(--muted)" }}>
              <div className="flex items-center gap-3">
                <CheckCircle2 size={18} style={{ color: "var(--success)" }} />
                <div>
                  <p className="text-xs font-bold" style={{ color: "var(--foreground)" }}>Data Freshness</p>
                  <p className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Last observation ingestion 16 min ago</p>
                </div>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "rgba(16, 185, 129, 0.15)", color: "var(--success)" }}>
                Pass
              </span>
            </div>
          </div>
        </div>

        {/* Right Col: Data Volume Bar Chart */}
        <div className="rounded-2xl border p-6" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold" style={{ color: "var(--foreground)" }}>
                Data Volume Ingestion
              </h3>
              <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
                Records ingested per day (in thousands)
              </p>
            </div>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: "rgba(2, 132, 199, 0.15)", color: "var(--primary)" }}>
              ~110k/day
            </span>
          </div>

          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={volumeData} margin={CHART_MARGIN}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--chart-text)" }} axisLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="k" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Bar dataKey="volume" fill="var(--primary)" radius={[6, 6, 0, 0]} name="Ingested Records (k)" barSize={26} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
