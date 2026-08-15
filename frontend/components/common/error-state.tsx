"use client";

import React from "react";
import { AlertTriangle, RefreshCw, ServerOff } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  compact?: boolean;
}

export function ErrorState({
  title = "Unable to load data",
  message = "Something went wrong while fetching the data. Please try again.",
  onRetry,
  compact = false,
}: ErrorStateProps) {
  if (compact) {
    return (
      <div className="flex items-center gap-3 rounded-lg border px-4 py-3 text-sm"
           style={{ borderColor: "var(--danger)", background: "var(--danger-muted)", color: "var(--foreground)" }}>
        <AlertTriangle size={16} style={{ color: "var(--danger)" }} />
        <span className="flex-1">{message}</span>
        {onRetry && (
          <button onClick={onRetry}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors hover:opacity-80"
                  style={{ background: "var(--danger)", color: "var(--danger-foreground)" }}>
            <RefreshCw size={12} /> Retry
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center rounded-xl border"
         style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <div className="p-4 rounded-full mb-4" style={{ background: "var(--danger-muted)" }}>
        <ServerOff size={28} style={{ color: "var(--danger)" }} />
      </div>
      <h3 className="text-base font-semibold mb-1" style={{ color: "var(--foreground)" }}>{title}</h3>
      <p className="text-sm max-w-sm" style={{ color: "var(--muted-foreground)" }}>{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90"
          style={{ background: "var(--primary)", color: "var(--primary-foreground)" }}
        >
          <RefreshCw size={14} /> Try Again
        </button>
      )}
    </div>
  );
}
