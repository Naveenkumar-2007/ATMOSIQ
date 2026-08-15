"use client";

import React from "react";
import { Map as MapIcon } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/common/empty-state";
import { useLocation } from "@/lib/location-context";

export default function WeatherMapPage() {
  const { currentLocation, locations } = useLocation();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Weather Map"
        description="Interactive weather map with observation stations"
        icon={<MapIcon size={20} />}
      />

      {/* Map Container */}
      <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="relative" style={{ height: "600px" }}>
          {/* Embedded OpenStreetMap iframe as lightweight fallback until Leaflet is installed */}
          <iframe
            src={`https://www.openstreetmap.org/export/embed.html?bbox=${(currentLocation?.longitude ?? 79.9) - 2}%2C${(currentLocation?.latitude ?? 15.5) - 2}%2C${(currentLocation?.longitude ?? 79.9) + 2}%2C${(currentLocation?.latitude ?? 15.5) + 2}&layer=mapnik&marker=${currentLocation?.latitude ?? 15.5}%2C${currentLocation?.longitude ?? 79.9}`}
            className="w-full h-full border-0"
            title="Weather Station Map"
            loading="lazy"
          />
          {/* Overlay with station info */}
          <div className="absolute top-4 left-4 rounded-xl border p-4 max-w-xs shadow-lg backdrop-blur-md"
               style={{ background: "var(--card)", borderColor: "var(--card-border)", opacity: 0.95 }}>
            <h3 className="text-sm font-semibold mb-2" style={{ color: "var(--foreground)" }}>Active Stations</h3>
            <div className="space-y-2">
              {locations.slice(0, 6).map((loc) => (
                <div key={loc.id} className="flex items-center gap-2 text-xs">
                  <span className="h-2 w-2 rounded-full shrink-0" style={{ background: loc.id === currentLocation?.id ? "var(--primary)" : "var(--success)" }} />
                  <span style={{ color: loc.id === currentLocation?.id ? "var(--primary)" : "var(--foreground)" }} className="font-medium">
                    {loc.name}
                  </span>
                  <span style={{ color: "var(--muted-foreground)" }} className="ml-auto">
                    {loc.latitude.toFixed(2)}°N, {loc.longitude.toFixed(2)}°E
                  </span>
                </div>
              ))}
              {locations.length > 6 && (
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>+{locations.length - 6} more stations</p>
              )}
            </div>
          </div>

          {/* Legend */}
          <div className="absolute bottom-4 right-4 rounded-lg border px-3 py-2 backdrop-blur-md"
               style={{ background: "var(--card)", borderColor: "var(--card-border)", opacity: 0.95 }}>
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--primary)" }} />
                <span style={{ color: "var(--muted-foreground)" }}>Selected</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full" style={{ background: "var(--success)" }} />
                <span style={{ color: "var(--muted-foreground)" }}>Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Station List */}
      <div className="rounded-xl border overflow-hidden" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="px-5 py-3 border-b" style={{ borderColor: "var(--border)" }}>
          <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>All Observation Stations ({locations.length})</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--muted)" }}>
                {["Station", "Latitude", "Longitude", "Timezone", "Status"].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left font-semibold" style={{ color: "var(--muted-foreground)" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {locations.map((loc) => (
                <tr key={loc.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}
                    className="transition-colors"
                    onMouseEnter={(e) => (e.currentTarget.style.background = "var(--card-hover)")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}>
                  <td className="px-4 py-2.5 font-medium" style={{ color: "var(--foreground)" }}>{loc.name}</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{loc.latitude.toFixed(4)}°N</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{loc.longitude.toFixed(4)}°E</td>
                  <td className="px-4 py-2.5" style={{ color: "var(--muted-foreground)" }}>{loc.timezone}</td>
                  <td className="px-4 py-2.5">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold"
                          style={{ background: "var(--success-muted)", color: "var(--success)" }}>
                      <span className="h-1.5 w-1.5 rounded-full" style={{ background: "var(--success)" }} />
                      Active
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
