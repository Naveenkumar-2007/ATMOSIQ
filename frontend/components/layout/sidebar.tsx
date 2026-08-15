"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CloudSun,
  Clock,
  CalendarDays,
  History,
  Map as MapIcon,
  Thermometer,
  CloudRain,
  Wind,
  GitCompareArrows,
  BarChart3,
  ClipboardCheck,
  ScrollText,
  Boxes,
  Database,
  Activity,
  Gauge,
  GraduationCap,
  Bell,
  HeartPulse,
  Settings,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api";

interface NavItem {
  title: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
}

interface NavGroup {
  groupName?: string;
  items: NavItem[];
  defaultOpen?: boolean;
}

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({});
  const [championCount, setChampionCount] = useState<number | null>(null);

  useEffect(() => {
    apiClient<{ champion_count: number }>("/api/v1/monitoring/summary")
      .then((d) => setChampionCount(d.champion_count))
      .catch(() => {});
  }, []);

  const navigation: NavGroup[] = [
    {
      items: [
        { title: "Overview", href: "/dashboard", icon: <LayoutDashboard size={18} /> },
      ],
    },
    {
      groupName: "Weather",
      defaultOpen: true,
      items: [
        { title: "Current Weather", href: "/weather/current", icon: <CloudSun size={18} /> },
        { title: "Hourly Forecast", href: "/weather/hourly", icon: <Clock size={18} /> },
        { title: "Daily Forecast", href: "/weather/daily", icon: <CalendarDays size={18} /> },
        { title: "Historical Weather", href: "/weather/history", icon: <History size={18} /> },
        { title: "Weather Map", href: "/weather/map", icon: <MapIcon size={18} /> },
      ],
    },
    {
      groupName: "AI Forecast",
      defaultOpen: true,
      items: [
        { title: "Temperature", href: "/forecast/temperature", icon: <Thermometer size={18} /> },
        { title: "Rainfall", href: "/forecast/rainfall", icon: <CloudRain size={18} /> },
        { title: "Wind", href: "/forecast/wind", icon: <Wind size={18} /> },
        { title: "Forecast Comparison", href: "/forecast/comparison", icon: <GitCompareArrows size={18} /> },
      ],
    },
    {
      groupName: "ML Intelligence",
      items: [
        { title: "Model Performance", href: "/ml/performance", icon: <BarChart3 size={18} /> },
        { title: "Forecast Verification", href: "/ml/verification", icon: <ClipboardCheck size={18} /> },
        { title: "Prediction History", href: "/ml/predictions", icon: <ScrollText size={18} /> },
        { title: "Models", href: "/ml/models", icon: <Boxes size={18} /> },
      ],
    },
    {
      groupName: "MLOps",
      items: [
        { title: "Data Quality", href: "/mlops/data-quality", icon: <Database size={18} /> },
        { title: "Drift Monitoring", href: "/mlops/drift", icon: <Activity size={18} /> },
        { title: "Model Monitoring", href: "/mlops/model-monitoring", icon: <Gauge size={18} /> },
        { title: "Training Runs", href: "/mlops/training-runs", icon: <GraduationCap size={18} /> },
        { title: "Alerts", href: "/mlops/alerts", icon: <Bell size={18} /> },
      ],
    },
    {
      groupName: "System",
      items: [
        { title: "System Health", href: "/system/health", icon: <HeartPulse size={18} /> },
        { title: "Settings", href: "/settings", icon: <Settings size={18} /> },
      ],
    },
  ];

  // Initialize open groups
  useEffect(() => {
    const initial: Record<string, boolean> = {};
    navigation.forEach((g) => {
      if (g.groupName) {
        const hasActive = g.items.some((item) => pathname === item.href || pathname.startsWith(`${item.href}/`));
        initial[g.groupName] = hasActive || g.defaultOpen || false;
      }
    });
    setOpenGroups(initial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  const toggleGroup = (name: string) => {
    setOpenGroups((prev) => ({ ...prev, [name]: !prev[name] }));
  };

  return (
    <aside
      className={cn(
        "h-screen sticky top-0 flex flex-col z-30 transition-all duration-300 select-none border-r",
        collapsed ? "w-16" : "w-60"
      )}
      style={{ background: "var(--sidebar-bg)", borderColor: "var(--sidebar-border)" }}
    >
      {/* Brand Header */}
      <div
        className="h-16 flex items-center justify-between px-4 border-b shrink-0"
        style={{ borderColor: "var(--sidebar-border)" }}
      >
        <Link href="/dashboard" className="flex items-center gap-2.5 overflow-hidden">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-sky-400 via-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-md shadow-sky-500/20 shrink-0">
            <CloudSun size={17} className="text-white" />
          </div>
          {!collapsed && (
            <div className="flex flex-col leading-none">
              <span className="text-[15px] font-bold tracking-tight" style={{ color: "var(--foreground)" }}>
                Atmos<span style={{ color: "var(--primary)" }}>IQ</span>
              </span>
              <span className="text-[9px] uppercase font-semibold tracking-wider mt-0.5" style={{ color: "var(--muted-foreground)" }}>
                AI Weather Intelligence
              </span>
            </div>
          )}
        </Link>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-md transition-colors"
          style={{ color: "var(--sidebar-text-muted)" }}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-1" role="navigation" aria-label="Main navigation">
        {navigation.map((group, idx) => (
          <div key={idx} className="space-y-0.5">
            {!collapsed && group.groupName && (
              <button
                onClick={() => toggleGroup(group.groupName!)}
                className="w-full flex items-center justify-between px-3 py-1.5 text-[10px] font-semibold tracking-wider uppercase rounded-md transition-colors hover:opacity-80"
                style={{ color: "var(--sidebar-group)" }}
              >
                <span>{group.groupName}</span>
                <ChevronDown
                  size={12}
                  className={cn("transition-transform", openGroups[group.groupName] ? "" : "-rotate-90")}
                />
              </button>
            )}
            {(collapsed || !group.groupName || openGroups[group.groupName!]) &&
              group.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-2.5 px-3 py-2 rounded-lg text-[12px] font-medium transition-all group relative",
                      isActive ? "font-semibold" : ""
                    )}
                    style={
                      isActive
                        ? {
                            background: "var(--sidebar-active-bg)",
                            color: "var(--sidebar-active-text)",
                            borderLeft: collapsed ? undefined : "2px solid var(--sidebar-active-border)",
                          }
                        : {
                            color: "var(--sidebar-text)",
                          }
                    }
                    title={collapsed ? item.title : undefined}
                    aria-current={isActive ? "page" : undefined}
                  >
                    <span
                      className="transition-transform group-hover:scale-110 shrink-0"
                      style={{ color: isActive ? "var(--sidebar-active-text)" : "var(--sidebar-text-muted)" }}
                    >
                      {item.icon}
                    </span>
                    {!collapsed && <span className="truncate">{item.title}</span>}
                    {!collapsed && item.badge && (
                      <span
                        className="ml-auto text-[10px] font-semibold px-1.5 py-0.5 rounded"
                        style={{ background: "var(--primary-muted)", color: "var(--primary)" }}
                      >
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            {idx < navigation.length - 1 && !collapsed && (
              <div className="my-2 mx-3 border-t" style={{ borderColor: "var(--border-subtle)" }} />
            )}
          </div>
        ))}
      </nav>

      {/* Bottom Status */}
      {!collapsed && (
        <div
          className="p-3 m-2 rounded-xl border text-xs"
          style={{ borderColor: "var(--card-border)", background: "var(--card)" }}
        >
          <div className="flex items-center gap-2 font-medium" style={{ color: "var(--success)" }}>
            <span className="relative flex h-2 w-2">
              <span
                className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                style={{ background: "var(--success)" }}
              />
              <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: "var(--success)" }} />
            </span>
            <span>{championCount !== null ? `${championCount} Champions Active` : "Loading..."}</span>
          </div>
          <p className="text-[11px] mt-1" style={{ color: "var(--muted-foreground)" }}>
            Quality Gate: Verified
          </p>
        </div>
      )}
    </aside>
  );
}
