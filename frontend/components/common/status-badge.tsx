"use client";

import React from "react";
import { cn } from "@/lib/utils";

type BadgeVariant = "healthy" | "warning" | "critical" | "degraded" | "info" | "champion" | "challenger" | "archived" | "development" | "default";

interface StatusBadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  dot?: boolean;
  className?: string;
}

const STYLES: Record<BadgeVariant, { bg: string; text: string; dot: string }> = {
  healthy:     { bg: "var(--success-muted)", text: "var(--success)", dot: "var(--status-healthy)" },
  champion:    { bg: "var(--success-muted)", text: "var(--success)", dot: "var(--status-healthy)" },
  warning:     { bg: "var(--warning-muted)", text: "var(--warning)", dot: "var(--status-warning)" },
  challenger:  { bg: "var(--warning-muted)", text: "var(--warning)", dot: "var(--status-warning)" },
  critical:    { bg: "var(--danger-muted)",  text: "var(--danger)",  dot: "var(--status-critical)" },
  degraded:    { bg: "var(--warning-muted)", text: "var(--status-degraded)", dot: "var(--status-degraded)" },
  info:        { bg: "var(--info-muted)",    text: "var(--info)",    dot: "var(--info)" },
  archived:    { bg: "var(--muted)",         text: "var(--muted-foreground)", dot: "var(--muted-foreground)" },
  development: { bg: "var(--muted)",         text: "var(--muted-foreground)", dot: "var(--muted-foreground)" },
  default:     { bg: "var(--muted)",         text: "var(--foreground)", dot: "var(--muted-foreground)" },
};

export function StatusBadge({ variant = "default", children, dot = true, className }: StatusBadgeProps) {
  const s = STYLES[variant] || STYLES.default;
  return (
    <span
      className={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold leading-none", className)}
      style={{ background: s.bg, color: s.text }}
    >
      {dot && (
        <span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ background: s.dot }} />
      )}
      {children}
    </span>
  );
}

/** Map model stage names to badge variants */
export function stageBadgeVariant(stage: string): BadgeVariant {
  switch (stage?.toLowerCase()) {
    case "champion": return "champion";
    case "challenger": return "challenger";
    case "archived": return "archived";
    case "development": return "development";
    default: return "default";
  }
}

/** Map alert severity to badge variant */
export function severityBadgeVariant(severity: string): BadgeVariant {
  switch (severity?.toLowerCase()) {
    case "critical": return "critical";
    case "warning": return "warning";
    case "info": return "info";
    default: return "default";
  }
}

/** Map health status to badge variant */
export function healthBadgeVariant(status: string): BadgeVariant {
  switch (status?.toLowerCase()) {
    case "healthy": return "healthy";
    case "degraded": return "degraded";
    case "down": return "critical";
    default: return "default";
  }
}
