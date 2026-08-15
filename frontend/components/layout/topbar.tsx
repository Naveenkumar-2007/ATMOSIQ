"use client";

import React, { useEffect, useState, useRef } from "react";
import {
  MapPin,
  Clock,
  Search,
  Bell,
  RefreshCw,
  Sun,
  Moon,
  ChevronDown,
  Globe,
  Plus
} from "lucide-react";
import { useLocation } from "@/lib/location-context";
import { useTheme } from "@/lib/theme-context";
import { apiClient } from "@/lib/api";

export function Topbar() {
  const { locationId, setLocationId, locations, triggerRefresh, addAndSelectLocation } = useLocation();
  const { theme, toggleTheme } = useTheme();
  const [timeStr, setTimeStr] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

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
    const interval = setInterval(update, 30000);
    return () => clearInterval(interval);
  }, []);

  // Handle outside click to close search dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Live Geocoding Search
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await apiClient<any[]>(`/api/v1/locations/search?q=${encodeURIComponent(searchQuery)}`);
        setSearchResults(results || []);
        setShowResults(true);
      } catch (e) {
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 350);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleSelectLocation = async (item: any) => {
    try {
      setShowResults(false);
      setSearchQuery("");
      const resp = await apiClient<any>("/api/v1/locations/onboard", {
        method: "POST",
        body: JSON.stringify({
          name: item.name,
          latitude: item.latitude,
          longitude: item.longitude,
          elevation: item.elevation || 0.0,
          timezone: item.timezone || "Asia/Kolkata",
          country: item.country,
        }),
      });
      const locData = resp?.location || {
        id: item.name.toLowerCase().replace(/[^a-z0-9]+/g, "_"),
        name: item.name,
        latitude: item.latitude,
        longitude: item.longitude,
        timezone: item.timezone || "Asia/Kolkata",
      };
      addAndSelectLocation(locData);
    } catch (e) {
      console.error("Failed to onboard station:", e);
    }
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    triggerRefresh();
    setTimeout(() => setIsRefreshing(false), 1500);
  };

  const currentLoc = locations.find((l) => l.id === locationId);

  return (
    <header
      className="h-14 backdrop-blur-md border-b px-4 sm:px-6 flex items-center justify-between z-30 sticky top-0"
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
        {/* Interactive Global Station Search */}
        <div className="relative hidden md:block" ref={searchRef}>
          <Search size={14} className="absolute left-3 top-2.5 z-10" style={{ color: "var(--muted-foreground)" }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => { if (searchResults.length > 0) setShowResults(true); }}
            placeholder="Search any global city/station..."
            className="h-9 w-60 rounded-lg border pl-9 pr-3 text-xs placeholder:text-[var(--muted-foreground)] focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium transition-all"
            style={{
              background: "var(--card)",
              borderColor: "var(--border)",
              color: "var(--foreground)",
            }}
          />

          {/* Search Dropdown Results */}
          {showResults && searchResults.length > 0 && (
            <div
              className="absolute right-0 top-11 w-80 rounded-2xl border shadow-2xl backdrop-blur-xl p-2 space-y-1 z-50 max-h-80 overflow-y-auto"
              style={{ background: "var(--card)", borderColor: "var(--card-border)" }}
            >
              <div className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-blue-500 flex items-center justify-between border-b" style={{ borderColor: "var(--border)" }}>
                <span>Global Stations Found ({searchResults.length})</span>
                <Globe size={12} />
              </div>
              {searchResults.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectLocation(item)}
                  className="w-full text-left p-2.5 rounded-xl hover:bg-blue-500/10 transition-colors flex items-center justify-between group cursor-pointer"
                >
                  <div>
                    <span className="text-xs font-bold block" style={{ color: "var(--foreground)" }}>
                      {item.name}
                    </span>
                    <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>
                      {item.admin1 ? `${item.admin1}, ` : ""}{item.country} · {item.latitude.toFixed(2)}°N, {item.longitude.toFixed(2)}°E
                    </span>
                  </div>
                  <div className="h-6 w-6 rounded-lg border flex items-center justify-center text-blue-500 group-hover:bg-blue-500 group-hover:text-white transition-colors" style={{ borderColor: "var(--border)" }}>
                    <Plus size={13} />
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="h-9 w-9 rounded-lg border flex items-center justify-center transition-colors cursor-pointer"
          style={{ borderColor: "var(--border)", background: "var(--card)", color: "var(--muted-foreground)" }}
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun size={15} className="text-amber-400" /> : <Moon size={15} className="text-slate-700" />}
        </button>

        {/* Refresh */}
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="h-9 px-3 rounded-lg border flex items-center gap-1.5 text-xs font-medium transition-colors disabled:opacity-50 cursor-pointer"
          style={{ borderColor: "var(--border)", background: "var(--card)", color: "var(--muted-foreground)" }}
          title="Refresh data"
          aria-label="Refresh data"
        >
          <RefreshCw size={14} className={isRefreshing ? "animate-spin" : ""} style={isRefreshing ? { color: "var(--primary)" } : {}} />
          <span className="hidden sm:inline">Sync</span>
        </button>

        {/* User Badge */}
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
