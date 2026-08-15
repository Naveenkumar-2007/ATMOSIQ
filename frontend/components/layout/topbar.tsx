"use client";

import React, { useEffect, useState } from "react";
import {
  MapPin,
  Clock,
  Search,
  Bell,
  RefreshCw,
  Sun,
  Moon,
  ChevronDown,
} from "lucide-react";
import { useLocation } from "@/lib/location-context";
import { useTheme } from "@/lib/theme-context";

export function Topbar() {
  const { locationId, setLocationId, locations, triggerRefresh } = useLocation();
  const { theme, toggleTheme } = useTheme();
  const [timeStr, setTimeStr] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTimeStr(
        now.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) +
        ", " +
        now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true }) +
        " IST"
      );
    };
    update();
    const interval = setInterval(update, 30000); // Update every 30s, not every 1s
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    triggerRefresh();
    setTimeout(() => setIsRefreshing(false), 1500);
  };

  const currentLoc = locations.find((l) => l.id === locationId);

  return (
    <header
      className="h-14 backdrop-blur-md border-b px-4 sm:px-6 flex items-center justify-between z-20 sticky top-0"
      style={{ background: "var(--header-bg)", borderColor: "var(--header-border)" }}
    >
      {/* Left: Location & Time */}
      <div className="flex items-center gap-3">
        {/* Location Dropdown */}
        <div
          className="flex items-center gap-2 rounded-lg px-3 py-1.5 border"
          style={{ background: "var(--card)", borderColor: "var(--border)" }}
        >
          <MapPin size={14} style={{ color: "var(--primary)" }} className="shrink-0" />
          <select
            value={locationId}
            onChange={(e) => setLocationId(e.target.value)}
            className="bg-transparent text-xs font-semibold focus:outline-none cursor-pointer pr-1 max-w-[200px]"
            style={{ color: "var(--foreground)" }}
            aria-label="Select location"
          >
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id} style={{ background: "var(--card)", color: "var(--foreground)" }}>
                {loc.name}
              </option>
            ))}
          </select>
        </div>

        {/* Real-time Clock */}
        <div className="hidden sm:flex items-center gap-1.5 text-xs" style={{ color: "var(--muted-foreground)" }}>
          <Clock size={13} />
          <span>{timeStr || "Loading..."}</span>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Search */}
        <div className="relative hidden lg:block">
          <Search size={14} className="absolute left-3 top-2.5" style={{ color: "var(--muted-foreground)" }} />
          <input
            type="text"
            placeholder="Search..."
            className="h-9 w-48 rounded-lg border pl-9 pr-3 text-xs placeholder:text-[var(--muted-foreground)] focus:outline-none focus:ring-1"
            style={{
              background: "var(--card)",
              borderColor: "var(--border)",
              color: "var(--foreground)",
            }}
          />
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="h-9 w-9 rounded-lg border flex items-center justify-center transition-colors"
          style={{ borderColor: "var(--border)", background: "var(--card)", color: "var(--muted-foreground)" }}
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
        </button>

        {/* Refresh */}
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="h-9 px-3 rounded-lg border flex items-center gap-1.5 text-xs font-medium transition-colors disabled:opacity-50"
          style={{ borderColor: "var(--border)", background: "var(--card)", color: "var(--muted-foreground)" }}
          title="Refresh data"
          aria-label="Refresh data"
        >
          <RefreshCw size={14} className={isRefreshing ? "animate-spin" : ""} style={isRefreshing ? { color: "var(--primary)" } : {}} />
          <span className="hidden sm:inline">Sync</span>
        </button>

        {/* Notification Bell */}
        <div className="relative">
          <button
            className="h-9 w-9 rounded-lg border flex items-center justify-center transition-colors"
            style={{ borderColor: "var(--border)", background: "var(--card)", color: "var(--muted-foreground)" }}
            aria-label="Notifications"
          >
            <Bell size={15} />
          </button>
          <span
            className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full ring-2"
            style={{ background: "var(--primary)" }}
          />
        </div>

        {/* User */}
        <div className="flex items-center gap-2 pl-2 border-l" style={{ borderColor: "var(--border)" }}>
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white text-xs font-semibold shadow-sm">
            AI
          </div>
          <div className="hidden xl:flex flex-col text-left leading-none">
            <span className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>AtmosIQ</span>
            <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>
              {currentLoc?.name || "Select location"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
