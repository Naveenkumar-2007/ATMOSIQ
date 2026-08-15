"use client";

import React from "react";
import { Inbox, Database, CloudOff, BarChart3 } from "lucide-react";

type EmptyVariant = "default" | "data" | "predictions" | "chart";

interface EmptyStateProps {
  title?: string;
  message?: string;
  variant?: EmptyVariant;
  action?: React.ReactNode;
}

const ICONS: Record<EmptyVariant, React.ReactNode> = {
  default: <Inbox size={28} />,
  data: <Database size={28} />,
  predictions: <CloudOff size={28} />,
  chart: <BarChart3 size={28} />,
};

export function EmptyState({
  title = "No data available",
  message = "There is no data to display for the current selection.",
  variant = "default",
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center rounded-xl border"
         style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <div className="p-4 rounded-full mb-4" style={{ background: "var(--muted)", color: "var(--muted-foreground)" }}>
        {ICONS[variant]}
      </div>
      <h3 className="text-base font-semibold mb-1" style={{ color: "var(--foreground)" }}>{title}</h3>
      <p className="text-sm max-w-sm" style={{ color: "var(--muted-foreground)" }}>{message}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
