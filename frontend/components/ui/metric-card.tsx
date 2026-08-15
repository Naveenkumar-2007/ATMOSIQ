import React from "react";
import { Card } from "./card";
import { cn } from "@/lib/utils";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  trend?: {
    value: string | number;
    direction: "up" | "down" | "neutral";
    label?: string;
  };
  icon?: React.ReactNode;
  accentColor?: "blue" | "sky" | "cyan" | "orange" | "emerald" | "rose" | "purple";
  className?: string;
  sparkline?: number[];
}

export function MetricCard({
  title,
  value,
  unit,
  subtitle,
  trend,
  icon,
  accentColor = "sky",
  className,
  sparkline,
}: MetricCardProps) {
  const accentClasses = {
    sky: "text-sky-400 bg-sky-500/10 border-sky-500/20",
    blue: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
    orange: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
    purple: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  };

  return (
    <Card className={cn("p-5 relative overflow-hidden group hover:border-slate-700/80 transition-all", className)}>
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</span>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className="text-2xl lg:text-3xl font-bold tracking-tight text-white font-sans">{value}</span>
            {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
          </div>
        </div>
        {icon && (
          <div className={cn("p-2.5 rounded-lg border", accentClasses[accentColor])}>
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between">
        {trend && (
          <div className="flex items-center gap-1.5 text-xs font-medium">
            {trend.direction === "up" && <ArrowUpRight size={14} className="text-emerald-400" />}
            {trend.direction === "down" && <ArrowDownRight size={14} className="text-rose-400" />}
            {trend.direction === "neutral" && <Minus size={14} className="text-slate-400" />}
            <span
              className={cn(
                trend.direction === "up" ? "text-emerald-400" : trend.direction === "down" ? "text-rose-400" : "text-slate-400"
              )}
            >
              {trend.value}
            </span>
            {trend.label && <span className="text-slate-400 font-normal">{trend.label}</span>}
          </div>
        )}
        {subtitle && <span className="text-xs text-slate-400">{subtitle}</span>}
      </div>
    </Card>
  );
}

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("animate-pulse rounded-md bg-slate-800/80", className)} {...props} />;
}

export function EmptyState({
  title,
  description,
  icon,
  action,
}: {
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-xl border border-dashed border-slate-800 bg-slate-900/40">
      {icon && <div className="p-3 mb-3 rounded-full bg-slate-800/80 text-slate-400">{icon}</div>}
      <h4 className="text-base font-semibold text-slate-200">{title}</h4>
      <p className="text-sm text-slate-400 max-w-sm mt-1">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
