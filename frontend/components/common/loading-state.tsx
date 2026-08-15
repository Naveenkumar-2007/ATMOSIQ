"use client";

import React from "react";
import { cn } from "@/lib/utils";

/* ── Skeleton ─────────────────────────────────────────────────── */

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return <div className={cn("skeleton", className)} />;
}

/* ── Card Skeleton ────────────────────────────────────────────── */

export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-xl border p-5 space-y-3", className)}
         style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-8 w-32" />
      <Skeleton className="h-3 w-20" />
    </div>
  );
}

/* ── Chart Skeleton ───────────────────────────────────────────── */

export function ChartSkeleton({ className, height = "h-64" }: { className?: string; height?: string }) {
  return (
    <div className={cn("rounded-xl border p-5 space-y-4", className)}
         style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-7 w-24 rounded-lg" />
      </div>
      <Skeleton className={cn("w-full rounded-lg", height)} />
    </div>
  );
}

/* ── Table Skeleton ───────────────────────────────────────────── */

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="rounded-xl border overflow-hidden"
         style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <div className="p-4 space-y-3">
        <div className="flex gap-4">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-4 w-24" />
        </div>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4 items-center pt-3 border-t" style={{ borderColor: "var(--border-subtle)" }}>
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-24" />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Page Skeleton ────────────────────────────────────────────── */

export function PageSkeleton() {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-7 w-48" />
          <Skeleton className="h-4 w-72" />
        </div>
        <Skeleton className="h-9 w-28 rounded-lg" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
      <ChartSkeleton />
      <TableSkeleton />
    </div>
  );
}
