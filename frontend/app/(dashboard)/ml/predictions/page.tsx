"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { EmptyState } from "@/components/common/empty-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { ScrollText, ChevronLeft, ChevronRight, Activity, Zap, CheckCircle2, Clock } from "lucide-react";

export default function PredictionHistoryPage() {
  const { locationId, locations } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [taskFilter, setTaskFilter] = useState("");
  const [locFilter, setLocFilter] = useState<string>("");
  const [page, setPage] = useState(0);
  const limit = 50;

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      const targetLoc = locFilter || locationId;
      if (targetLoc && targetLoc !== "all") params.set("location", targetLoc);
      if (taskFilter) params.set("task", taskFilter);
      params.set("limit", limit.toString());
      params.set("offset", (page * limit).toString());
      const res = await apiClient<any>(`/api/v1/ml/predictions?${params}`);
      setData(res);
    } catch (e: any) {
      setError(e.message || "Failed to load prediction history");
    } finally {
      setIsLoading(false);
    }
  }, [locationId, locFilter, taskFilter, page]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  const rows = data?.rows || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Prediction History"
        description={`${total} live predictions recorded in PostgreSQL`}
        icon={<ScrollText size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        <div className="flex flex-wrap items-center gap-2">
          {/* Location Filter */}
          <select
            value={locFilter}
            onChange={(e) => { setLocFilter(e.target.value); setPage(0); }}
            className="text-xs rounded-lg border px-3 py-1.5 font-medium"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <option value="all">All Locations</option>
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </select>

          {/* Task Filter */}
          <select
            value={taskFilter}
            onChange={(e) => { setTaskFilter(e.target.value); setPage(0); }}
            className="text-xs rounded-lg border px-3 py-1.5 font-medium"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <option value="">All Tasks</option>
            {[
              "temperature",
              "humidity",
              "pressure",
              "wind_speed",
              "rain_occurrence",
              "precipitation_amount"
            ].map((t) => (
              <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
            ))}
          </select>
        </div>
      </PageHeader>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>Total Predictions</p>
          <p className="text-2xl font-bold mt-1" style={{ color: "var(--primary)" }}>{total.toLocaleString()}</p>
        </div>
        <div className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>Current Page Rows</p>
          <p className="text-2xl font-bold mt-1" style={{ color: "var(--chart-blue)" }}>{rows.length}</p>
        </div>
        <div className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>Tasks Covered</p>
          <p className="text-2xl font-bold mt-1" style={{ color: "var(--chart-emerald)" }}>6 Tasks</p>
        </div>
        <div className="rounded-xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <p className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>Status</p>
          <p className="text-2xl font-bold mt-1" style={{ color: "var(--success)" }}>Active Engine</p>
        </div>
      </div>

      {rows.length > 0 ? (
        <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
            <table className="w-full text-xs">
              <thead className="sticky top-0 z-10" style={{ background: "var(--muted)" }}>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Task", "Location", "Issue Time", "Valid Time", "Horizon", "Prediction", "Model"].map((h) => (
                    <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r: any) => (
                  <tr
                    key={r.id}
                    style={{ borderBottom: "1px solid var(--border-subtle)" }}
                    className="transition-colors"
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                  >
                    <td className="px-4 py-2 font-medium capitalize" style={{ color: "var(--foreground)" }}>
                      {r.task?.replace(/_/g, " ")}
                    </td>
                    <td className="px-4 py-2 font-semibold capitalize" style={{ color: "var(--foreground)" }}>
                      {r.location_id}
                    </td>
                    <td className="px-4 py-2" style={{ color: "var(--muted-foreground)" }}>
                      {new Date(r.issue_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
                    </td>
                    <td className="px-4 py-2" style={{ color: "var(--foreground)" }}>
                      {new Date(r.valid_time).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
                    </td>
                    <td className="px-4 py-2 font-mono" style={{ color: "var(--muted-foreground)" }}>
                      {r.horizon_hours}h
                    </td>
                    <td className="px-4 py-2 font-bold" style={{ color: "var(--chart-blue)" }}>
                      {r.payload?.prediction != null ? Number(r.payload.prediction).toFixed(2) : "—"}
                    </td>
                    <td className="px-4 py-2 font-mono text-[10px]" style={{ color: "var(--muted-foreground)" }}>
                      {r.model_version_id?.slice(0, 16) || "Champion"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between px-5 py-3 border-t" style={{ borderColor: "var(--border)" }}>
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              Showing {page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total}
            </p>
            <div className="flex gap-1">
              <button
                onClick={() => setPage(Math.max(0, page - 1))}
                disabled={page === 0}
                className="p-1.5 rounded-md border disabled:opacity-30"
                style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
              >
                <ChevronLeft size={14} />
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                disabled={page >= totalPages - 1}
                className="p-1.5 rounded-md border disabled:opacity-30"
                style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <EmptyState title="No predictions found" message="Try selecting 'All Locations' or another task filter." variant="predictions" />
      )}
    </div>
  );
}
