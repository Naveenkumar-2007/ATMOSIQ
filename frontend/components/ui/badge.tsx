import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info" | "purple" | "outline";
}

export function Badge({ className, variant = "default", children, ...props }: BadgeProps) {
  const variants = {
    default: "bg-slate-800 text-slate-300 border-slate-700",
    success: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    warning: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    danger: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    info: "bg-sky-500/15 text-sky-400 border-sky-500/30",
    purple: "bg-purple-500/15 text-purple-400 border-purple-500/30",
    outline: "bg-transparent text-slate-300 border-slate-700",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium border tracking-wide",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export interface StatusIndicatorProps {
  status: "healthy" | "warning" | "critical" | "offline" | "active";
  label?: string;
  size?: "sm" | "md";
}

export function StatusIndicator({ status, label, size = "md" }: StatusIndicatorProps) {
  const colors = {
    healthy: "bg-emerald-400 shadow-emerald-400/50",
    active: "bg-sky-400 shadow-sky-400/50",
    warning: "bg-amber-400 shadow-amber-400/50",
    critical: "bg-rose-400 shadow-rose-400/50",
    offline: "bg-slate-500 shadow-slate-500/50",
  };

  const dotSize = size === "sm" ? "h-1.5 w-1.5" : "h-2 w-2";

  return (
    <div className="inline-flex items-center gap-2">
      <span className="relative flex h-2.5 w-2.5 items-center justify-center">
        <span className={cn("animate-ping absolute inline-flex h-full w-full rounded-full opacity-75", colors[status])} />
        <span className={cn("relative inline-flex rounded-full shadow-sm", dotSize, colors[status])} />
      </span>
      {label && <span className="text-xs font-medium text-slate-300">{label}</span>}
    </div>
  );
}
