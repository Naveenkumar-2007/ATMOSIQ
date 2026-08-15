"use client";

import React, { useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { StatusBadge } from "@/components/common/status-badge";
import { Database } from "lucide-react";

export default function DataQualityPage() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true); setError(null);
    try { setData(await apiClient<any>("/api/v1/mlops/data-quality")); }
    catch (e: any) { setError(e.message || "Failed"); } finally { setIsLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const checks = data?.checks || data?.quality_checks || [];
  const summary = data?.summary || {};

  return (
    <div className="space-y-6">
      <PageHeader title="Data Quality" description="Automated data quality checks and validation results" icon={<Database size={20} />} onRefresh={fetchData} isLoading={isLoading} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MC label="Total Checks" value={summary.total_checks?.toString() || checks.length.toString()} color="var(--primary)" />
        <MC label="Passed" value={summary.passed?.toString() || checks.filter((c: any) => c.passed || c.status === "passed").length.toString()} color="var(--success)" />
        <MC label="Failed" value={summary.failed?.toString() || checks.filter((c: any) => !c.passed && c.status !== "passed").length.toString()} color="var(--danger)" />
        <MC label="Coverage" value={summary.coverage ? `${(summary.coverage * 100).toFixed(0)}%` : "—"} color="var(--chart-violet)" />
      </div>

      {checks.length > 0 && (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--muted)" }}>
                  {["Check", "Column", "Status", "Details", "Timestamp"].map(h => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {checks.map((c: any, i: number) => (
                  <tr key={i} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td className="px-4 py-2 font-medium" style={{ color: "var(--foreground)" }}>{c.check_name || c.name || `Check ${i+1}`}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{c.column || "—"}</td>
                    <td className="px-4 py-2">
                      <StatusBadge variant={c.passed || c.status === "passed" ? "healthy" : "critical"}>
                        {c.passed || c.status === "passed" ? "Passed" : "Failed"}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{c.details || c.message || "—"}</td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>{c.timestamp ? new Date(c.timestamp).toLocaleString("en-IN", { day:"2-digit", month:"short", hour:"2-digit" }) : "—"}</td>
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

function MC({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
      <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{label}</p>
      <p className="text-xl font-bold mt-1" style={{ color }}>{value}</p>
    </div>
  );
}
