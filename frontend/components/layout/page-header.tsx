"use client";

import React from "react";
import { RefreshCw, Download } from "lucide-react";

interface PageHeaderProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  onRefresh?: () => void;
  onExport?: () => void;
  isLoading?: boolean;
  lastUpdated?: string;
  children?: React.ReactNode;
}

export function PageHeader({
  title,
  description,
  icon,
  onRefresh,
  onExport,
  isLoading,
  lastUpdated,
  children,
}: PageHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
      <div className="flex items-start gap-3">
        {icon && (
          <div className="p-2.5 rounded-xl shrink-0" style={{ background: "var(--primary-muted)", color: "var(--primary)" }}>
            {icon}
          </div>
        )}
        <div>
          <h1 className="text-xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>
            {title}
          </h1>
          {description && (
            <p className="text-sm mt-0.5" style={{ color: "var(--muted-foreground)" }}>
              {description}
            </p>
          )}
          {lastUpdated && (
            <p className="text-xs mt-1" style={{ color: "var(--muted-foreground)" }}>
              Last updated: {lastUpdated}
            </p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {children}
        {onExport && (
          <button
            onClick={onExport}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg border text-xs font-medium transition-colors"
            style={{ borderColor: "var(--border)", color: "var(--muted-foreground)", background: "var(--card)" }}
          >
            <Download size={14} /> Export
          </button>
        )}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg border text-xs font-medium transition-colors disabled:opacity-50"
            style={{ borderColor: "var(--border)", color: "var(--muted-foreground)", background: "var(--card)" }}
            title="Refresh data"
          >
            <RefreshCw size={14} className={isLoading ? "animate-spin" : ""} /> Refresh
          </button>
        )}
      </div>
    </div>
  );
}
