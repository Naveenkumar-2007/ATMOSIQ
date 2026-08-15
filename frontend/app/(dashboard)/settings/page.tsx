"use client";

import React from "react";
import { useTheme } from "@/lib/theme-context";
import { useLocation } from "@/lib/location-context";
import { PageHeader } from "@/components/layout/page-header";
import { Settings as SettingsIcon, Sun, Moon, MapPin, Palette, Globe } from "lucide-react";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { locationId, setLocationId, locations } = useLocation();

  return (
    <div className="space-y-6 max-w-3xl">
      <PageHeader title="Settings" description="Platform preferences and configuration" icon={<SettingsIcon size={20} />} />

      {/* Appearance */}
      <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="flex items-center gap-3 mb-4">
          <Palette size={18} style={{ color: "var(--primary)" }} />
          <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>Appearance</h3>
        </div>
        <div className="flex gap-3">
          {(["dark", "light"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className="flex items-center gap-2 px-4 py-3 rounded-xl border transition-all"
              style={{
                borderColor: theme === t ? "var(--primary)" : "var(--border)",
                background: theme === t ? "var(--primary-muted)" : "var(--card)",
              }}
            >
              {t === "dark" ? <Moon size={16} style={{ color: "var(--primary)" }} /> : <Sun size={16} style={{ color: "var(--chart-amber)" }} />}
              <span className="text-sm font-medium capitalize" style={{ color: "var(--foreground)" }}>{t} Mode</span>
            </button>
          ))}
        </div>
      </div>

      {/* Default Location */}
      <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="flex items-center gap-3 mb-4">
          <MapPin size={18} style={{ color: "var(--primary)" }} />
          <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>Default Location</h3>
        </div>
        <select
          value={locationId}
          onChange={(e) => setLocationId(e.target.value)}
          className="w-full max-w-sm rounded-lg border px-4 py-2.5 text-sm font-medium"
          style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
        >
          {locations.map((loc) => (
            <option key={loc.id} value={loc.id}>{loc.name} — {loc.latitude.toFixed(2)}°N, {loc.longitude.toFixed(2)}°E</option>
          ))}
        </select>
        <p className="text-xs mt-2" style={{ color: "var(--muted-foreground)" }}>
          This location will be used as the default across all weather and forecast pages.
        </p>
      </div>

      {/* API Configuration */}
      <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="flex items-center gap-3 mb-4">
          <Globe size={18} style={{ color: "var(--primary)" }} />
          <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>API Configuration</h3>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: "var(--border-subtle)" }}>
            <span className="text-sm" style={{ color: "var(--muted-foreground)" }}>API Base URL</span>
            <code className="text-xs px-2 py-1 rounded" style={{ background: "var(--muted)", color: "var(--foreground)" }}>
              {typeof window !== "undefined" ? (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000") : "http://127.0.0.1:8000"}
            </code>
          </div>
          <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: "var(--border-subtle)" }}>
            <span className="text-sm" style={{ color: "var(--muted-foreground)" }}>Refresh Interval</span>
            <span className="text-sm font-medium" style={{ color: "var(--foreground)" }}>Manual</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm" style={{ color: "var(--muted-foreground)" }}>Data Source</span>
            <span className="text-sm font-medium" style={{ color: "var(--foreground)" }}>Open-Meteo (ERA5)</span>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--foreground)" }}>About AtmosIQ</h3>
        <div className="space-y-1 text-xs" style={{ color: "var(--muted-foreground)" }}>
          <p>AI-Powered Weather Intelligence & MLOps Platform</p>
          <p>Built with Next.js 16, FastAPI, SQLAlchemy, LightGBM, XGBoost, CatBoost, LSTM, TCN</p>
          <p>Data providers: Open-Meteo ERA5, Weatherbit, Visual Crossing</p>
        </div>
      </div>
    </div>
  );
}
