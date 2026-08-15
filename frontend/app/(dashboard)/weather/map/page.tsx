"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import {
  MapPin, Play, Pause, SkipBack, SkipForward, Maximize2,
  Thermometer, CloudRain, Wind, Droplets, Cloud, Gauge,
  AlertTriangle, Info, RefreshCw, Layers, Compass, Eye, ShieldCheck
} from "lucide-react";

type MapLayer = "Rainfall" | "Temperature" | "Wind" | "Humidity" | "Cloud Cover" | "Pressure";
type MapType = "Standard" | "Satellite" | "Dark" | "Terrain";

const TIMELINE_STEPS = [
  "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM"
];

export default function WeatherMapPage() {
  const { locationId, currentLocation, locations, setLocationId, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeLayer, setActiveLayer] = useState<MapLayer>("Rainfall");
  const [timelineIdx, setTimelineIdx] = useState<number>(3); // 10:00 AM default
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [mapType, setMapType] = useState<MapType>("Standard");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/weather/combined/${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load weather map data");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  // Play animation loop
  useEffect(() => {
    if (!isPlaying) return;
    const timer = setInterval(() => {
      setTimelineIdx((prev) => (prev + 1) % TIMELINE_STEPS.length);
    }, 1400);
    return () => clearInterval(timer);
  }, [isPlaying]);

  const curr = data?.current || {};
  const loc = data?.location || currentLocation || {};

  const temp = curr?.temperature_2m ?? 28.0;
  const rainfall = curr?.summary?.rainfall ?? (curr?.precipitation ?? 0.0);
  const windSpeed = curr?.wind_speed_10m ?? 12.0;
  const humidity = curr?.relative_humidity_2m ?? 65.0;

  const centerLat = Number(loc?.latitude ?? 15.48);
  const centerLng = Number(loc?.longitude ?? 79.91);
  const centerName = loc?.name ?? currentLocation?.name ?? locationId;
  const obsTime = new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });

  // Map Tile URL based on selected Map Type & Coordinates
  const mapIframeUrl = useMemo(() => {
    const bbox = `${centerLng - 2.5}%2C${centerLat - 2.0}%2C${centerLng + 2.5}%2C${centerLat + 2.0}`;
    if (mapType === "Dark") {
      return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${centerLat}%2C${centerLng}`;
    }
    if (mapType === "Satellite") {
      return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=cyclemap&marker=${centerLat}%2C${centerLng}`;
    }
    if (mapType === "Terrain") {
      return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=transportmap&marker=${centerLat}%2C${centerLng}`;
    }
    return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${centerLat}%2C${centerLng}`;
  }, [mapType, centerLat, centerLng]);

  // Layer Configuration (Legends, Gradients, Units)
  const layerConfig = useMemo(() => {
    switch (activeLayer) {
      case "Temperature":
        return {
          title: "Surface Air Temperature (°C)",
          unit: "°C",
          gradient: "from-blue-600 via-emerald-400 via-amber-400 via-orange-500 to-rose-600",
          ticks: ["15°", "22°", "28°", "34°", "40°", "46°"],
          overlayColor: "rgba(239, 68, 68, 0.18)",
        };
      case "Wind":
        return {
          title: "Wind Velocity & Streamlines (km/h)",
          unit: "km/h",
          gradient: "from-teal-300 via-cyan-400 via-blue-500 via-indigo-600 to-purple-700",
          ticks: ["0", "10", "20", "30", "45", "60+"],
          overlayColor: "rgba(14, 165, 233, 0.16)",
        };
      case "Humidity":
        return {
          title: "Relative Humidity (%)",
          unit: "%",
          gradient: "from-amber-200 via-yellow-300 via-emerald-400 via-teal-500 to-blue-700",
          ticks: ["20%", "40%", "60%", "75%", "90%", "100%"],
          overlayColor: "rgba(6, 182, 212, 0.16)",
        };
      case "Cloud Cover":
        return {
          title: "Infrared Cloud Density (%)",
          unit: "%",
          gradient: "from-slate-200 via-slate-400 via-slate-600 via-indigo-500 to-purple-800",
          ticks: ["0%", "20%", "40%", "60%", "80%", "100%"],
          overlayColor: "rgba(100, 116, 139, 0.22)",
        };
      case "Pressure":
        return {
          title: "Mean Sea Level Pressure (hPa)",
          unit: "hPa",
          gradient: "from-violet-600 via-blue-500 via-emerald-400 via-amber-400 to-rose-500",
          ticks: ["995", "1002", "1008", "1014", "1020", "1026"],
          overlayColor: "rgba(168, 85, 247, 0.16)",
        };
      default: // Rainfall
        return {
          title: "Radar Precipitation Echo (mm/h)",
          unit: "mm",
          gradient: "from-blue-400 via-emerald-400 via-yellow-400 via-orange-500 via-purple-600 to-rose-600",
          ticks: ["0.0", "1.0", "3.0", "6.0", "12.0", "25.0+"],
          overlayColor: "rgba(2, 132, 199, 0.22)",
        };
    }
  }, [activeLayer]);

  if (isLoading) return <PageSkeleton />;
  if (error && !data) return <ErrorState title="Unable to load weather map" message={error} onRetry={fetchData} />;

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Main Map Controls */}
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>Weather Radar & Synoptic Map</h1>
            <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
              Multi-layer atmospheric radar, regional telemetry & live satellite overlays · {centerName}
            </p>
          </div>
        </div>

        {/* Player Controls Bar */}
        <div className="rounded-2xl border p-4 space-y-3" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex flex-wrap items-center justify-between gap-3">
            {/* Left Layer Selectors */}
            <div className="flex flex-wrap items-center gap-3 text-xs">
              <div className="flex items-center gap-2">
                <span className="font-semibold" style={{ color: "var(--muted-foreground)" }}>Map Layer:</span>
                <div className="flex rounded-xl border p-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
                  {(["Rainfall", "Temperature", "Wind", "Humidity", "Cloud Cover", "Pressure"] as MapLayer[]).map((l) => (
                    <button
                      key={l}
                      onClick={() => setActiveLayer(l)}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                        activeLayer === l ? "bg-blue-600 text-white shadow" : "hover:text-blue-500"
                      }`}
                      style={{ color: activeLayer === l ? "#ffffff" : "var(--muted-foreground)" }}
                    >
                      {l}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="font-semibold" style={{ color: "var(--muted-foreground)" }}>Time:</span>
                <span className="px-3 py-1.5 rounded-lg border font-mono font-semibold" style={{ background: "var(--muted)", borderColor: "var(--border)", color: "var(--foreground)" }}>
                  15 Aug 2026, {TIMELINE_STEPS[timelineIdx]}
                </span>
              </div>
            </div>

            {/* Middle Playback Controls */}
            <div className="flex items-center gap-1.5 p-1 rounded-xl border" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <button
                onClick={() => setTimelineIdx((prev) => Math.max(0, prev - 1))}
                className="p-1.5 rounded-lg hover:bg-black/10 dark:hover:bg-white/10 transition-colors cursor-pointer"
                style={{ color: "var(--foreground)" }}
                title="Step Backward"
              >
                <SkipBack size={14} />
              </button>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold transition-colors flex items-center gap-1 text-xs shadow cursor-pointer"
              >
                {isPlaying ? <Pause size={13} /> : <Play size={13} />}
                <span>{isPlaying ? "Pause" : "Play Radar"}</span>
              </button>
              <button
                onClick={() => setTimelineIdx((prev) => Math.min(TIMELINE_STEPS.length - 1, prev + 1))}
                className="p-1.5 rounded-lg hover:bg-black/10 dark:hover:bg-white/10 transition-colors cursor-pointer"
                style={{ color: "var(--foreground)" }}
                title="Step Forward"
              >
                <SkipForward size={14} />
              </button>
            </div>

            {/* Right Map Type Selection */}
            <div className="flex items-center gap-2 text-xs">
              <span className="font-semibold" style={{ color: "var(--muted-foreground)" }}>Basemap:</span>
              <select
                value={mapType}
                onChange={(e) => setMapType(e.target.value as MapType)}
                className="rounded-lg border px-3 py-1.5 font-semibold focus:outline-none cursor-pointer"
                style={{ background: "var(--muted)", borderColor: "var(--border)", color: "var(--foreground)" }}
              >
                <option value="Standard">Standard Map</option>
                <option value="Satellite">Satellite / Terrain</option>
                <option value="Dark">Dark Matter</option>
                <option value="Terrain">Topographic Contours</option>
              </select>
            </div>
          </div>

          {/* Timeline Slider Track */}
          <div className="pt-2 border-t" style={{ borderColor: "var(--border)" }}>
            <div className="relative flex items-center justify-between px-2">
              <div className="absolute left-0 right-0 h-1.5 rounded-full z-0" style={{ background: "var(--border)" }} />
              <div
                className="absolute left-0 h-1.5 bg-blue-500 rounded-full z-0 transition-all"
                style={{ width: `${(timelineIdx / (TIMELINE_STEPS.length - 1)) * 100}%` }}
              />
              {TIMELINE_STEPS.map((step, idx) => (
                <button
                  key={step}
                  onClick={() => setTimelineIdx(idx)}
                  className="flex flex-col items-center gap-1 z-10 focus:outline-none group cursor-pointer"
                >
                  <div
                    className={`w-3.5 h-3.5 rounded-full transition-all ${
                      idx === timelineIdx
                        ? "bg-blue-500 ring-4 ring-blue-500/20 scale-125 shadow-lg"
                        : idx < timelineIdx
                        ? "bg-blue-400"
                        : "bg-slate-400 group-hover:bg-slate-500"
                    }`}
                  />
                  <span className={`text-[10px] font-mono mt-1 ${idx === timelineIdx ? "font-bold text-blue-500" : ""}`} style={{ color: idx === timelineIdx ? undefined : "var(--muted-foreground)" }}>
                    {step}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Interactive Weather Map Canvas */}
      <div className="relative w-full rounded-2xl overflow-hidden border shadow-2xl" style={{ height: "520px", background: "var(--muted)", borderColor: "var(--card-border)" }}>
        {/* Dynamic Basemap Iframe */}
        <iframe
          src={mapIframeUrl}
          className={`w-full h-full border-0 transition-opacity duration-500 ${
            mapType === "Dark" ? "invert-[0.9] hue-rotate-180 brightness-90 contrast-125" : "opacity-90"
          }`}
          title="Live Weather Map Canvas"
          loading="lazy"
        />

        {/* Dynamic Weather Layer Overlay Heatmap / Radar Grid */}
        <div
          className="absolute inset-0 pointer-events-none transition-all duration-700 backdrop-blur-[0.5px]"
          style={{ background: layerConfig.overlayColor }}
        >
          {/* Animated Atmospheric Streamlines */}
          <div className="w-full h-full opacity-35 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:24px_24px] animate-pulse" />
        </div>

        {/* Center Station Pulse Marker */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center pointer-events-none z-10">
          <div className="relative flex items-center justify-center">
            <div className="w-12 h-12 rounded-full bg-blue-500/30 animate-ping absolute" />
            <div className="w-4 h-4 rounded-full bg-blue-500 border-2 border-white shadow-xl z-10" />
          </div>
          <span className="mt-1 px-3 py-0.5 rounded-full text-[10px] font-bold border shadow-lg backdrop-blur-md" style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}>
            {centerName}
          </span>
        </div>

        {/* Floating Station Telemetry Card (Top Right) - Completely Dynamic based on current station */}
        <div className="absolute top-4 right-4 p-4 rounded-2xl border shadow-2xl backdrop-blur-xl z-20 w-72 space-y-3" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-blue-500 uppercase tracking-wider block">Live Weather Station</span>
              <h4 className="text-sm font-extrabold leading-tight" style={{ color: "var(--foreground)" }}>
                {centerName}
              </h4>
            </div>
            <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">
              Active
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 rounded-xl border space-y-0.5" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
                <Thermometer size={12} className="text-rose-500" /> Temperature
              </span>
              <p className="text-base font-extrabold" style={{ color: "var(--foreground)" }}>
                {temp.toFixed(1)}°C
              </p>
            </div>

            <div className="p-2.5 rounded-xl border space-y-0.5" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
                <CloudRain size={12} className="text-blue-500" /> Rainfall
              </span>
              <p className="text-base font-extrabold text-blue-500">
                {rainfall.toFixed(1)} mm
              </p>
            </div>

            <div className="p-2.5 rounded-xl border space-y-0.5" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
                <Wind size={12} className="text-teal-500" /> Wind Velocity
              </span>
              <p className="text-base font-extrabold" style={{ color: "var(--foreground)" }}>
                {windSpeed.toFixed(0)} km/h
              </p>
            </div>

            <div className="p-2.5 rounded-xl border space-y-0.5" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
              <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
                <Droplets size={12} className="text-cyan-500" /> Humidity
              </span>
              <p className="text-base font-extrabold" style={{ color: "var(--foreground)" }}>
                {humidity.toFixed(0)}%
              </p>
            </div>
          </div>

          <div className="flex items-center justify-between text-[9px] font-mono pt-2 border-t" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}>
            <span>Lat: {centerLat.toFixed(2)}°N, Lng: {centerLng.toFixed(2)}°E</span>
            <span>{obsTime} IST</span>
          </div>
        </div>

        {/* Bottom-left Dynamic Radar Legend Scale */}
        <div className="absolute bottom-4 left-4 p-3 rounded-2xl border shadow-2xl backdrop-blur-xl z-20 space-y-1.5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center justify-between text-[10px] font-bold" style={{ color: "var(--foreground)" }}>
            <span>{layerConfig.title}</span>
            <span className="text-blue-500 font-mono">{activeLayer}</span>
          </div>
          <div className={`h-2.5 w-64 rounded-full bg-gradient-to-r ${layerConfig.gradient} shadow-inner`} />
          <div className="flex justify-between text-[8px] font-mono font-semibold px-0.5" style={{ color: "var(--muted-foreground)" }}>
            {layerConfig.ticks.map((t, idx) => (
              <span key={idx}>{t}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Regional Station Network Table (Dynamically rendered from active DB locations) */}
      <div className="rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Active Meteorological Stations Network</h3>
            <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
              Synchronized automated weather stations (AWS) telemetry ({locations.length} Stations Available)
            </p>
          </div>
          <span className="text-xs font-semibold text-blue-500">{locations.length} Stations Registered</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b text-left font-semibold" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}>
                <th className="py-2.5 px-3">Station Name</th>
                <th className="py-2.5 px-3">Coordinates</th>
                <th className="py-2.5 px-3">Timezone</th>
                <th className="py-2.5 px-3 text-right">Status</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y font-medium" style={{ borderColor: "var(--border)" }}>
              {locations.map((st) => {
                const isSelected = st.id === locationId;
                return (
                  <tr
                    key={st.id}
                    onClick={() => setLocationId(st.id)}
                    className={`transition-colors cursor-pointer ${
                      isSelected ? "bg-blue-500/10 font-bold" : "hover:bg-black/5 dark:hover:bg-white/5"
                    }`}
                  >
                    <td className="py-2.5 px-3 flex items-center gap-1.5" style={{ color: "var(--foreground)" }}>
                      <MapPin size={13} className={isSelected ? "text-blue-500" : "text-slate-400"} />
                      <span>{st.name}</span>
                      {isSelected && <span className="text-[9px] px-1.5 py-0.2 rounded bg-blue-500 text-white">Active</span>}
                    </td>
                    <td className="py-2.5 px-3 font-mono" style={{ color: "var(--muted-foreground)" }}>
                      {Number(st.latitude).toFixed(2)}°N, {Number(st.longitude).toFixed(2)}°E
                    </td>
                    <td className="py-2.5 px-3" style={{ color: "var(--muted-foreground)" }}>
                      {st.timezone || "Asia/Kolkata"}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">
                        Online
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button className="px-2 py-0.5 rounded-lg border text-[10px] font-bold text-blue-500 hover:bg-blue-500 hover:text-white transition-colors" style={{ borderColor: "var(--border)" }}>
                        {isSelected ? "Selected" : "Select"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
