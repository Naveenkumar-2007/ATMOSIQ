"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton, CardSkeleton } from "@/components/common/loading-state";
import { StatusBadge, healthBadgeVariant, stageBadgeVariant } from "@/components/common/status-badge";
import { WeatherIcon } from "@/components/ui/weather-icon";
import {
  LayoutDashboard, Thermometer, Droplets, Wind, Eye, Gauge, CloudSun,
  ArrowUp, ArrowDown, TrendingUp, Cpu, ArrowRight, BarChart3,
} from "lucide-react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ComposedChart, Bar, Line,
} from "recharts";
import { CHART_TOOLTIP_STYLE, CHART_MARGIN, SERIES_COLORS, chartHeight } from "@/lib/chart-theme";

function weatherCondition(code: number): string {
  if (code === 0) return "Clear Sky";
  if (code <= 2) return "Partly Cloudy";
  if (code === 3) return "Overcast";
  if (code <= 49) return "Foggy";
  if (code <= 59) return "Drizzle";
  if (code <= 69) return "Rain";
  if (code <= 79) return "Snow";
  return "Thunderstorm";
}

function windDirection(deg: number): string {
  const dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  return dirs[Math.round(deg / 22.5) % 16] || "N";
}

export default function DashboardPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [weather, setWeather] = useState<any>(null);
  const [hourlyChart, setHourlyChart] = useState<any[]>([]);
  const [dailyData, setDailyData] = useState<any[]>([]);
  const [monitoring, setMonitoring] = useState<any>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch all dashboard data in parallel
      const [combined, monitoringResp, healthResp] = await Promise.allSettled([
        apiClient<any>(`/api/v1/weather/combined/${locationId}`),
        apiClient<any>("/api/v1/monitoring/summary"),
        apiClient<any>("/api/v1/system/health"),
      ]);

      if (combined.status === "fulfilled") {
        const c = combined.value;
        setWeather(c.current);

        // Hourly chart (next 24h)
        const h = c.hourly;
        if (h?.times) {
          setHourlyChart(h.times.slice(0, 24).map((t: string, i: number) => ({
            time: new Date(t).toLocaleTimeString("en-IN", { hour: "numeric", hour12: true }),
            temperature: h.temperature_2m?.[i],
            precipitation: h.precipitation?.[i] ?? 0,
            rainProb: h.precipitation_probability?.[i] ?? 0,
          })));
        }

        // Daily data
        const d = c.daily;
        if (d?.dates) {
          setDailyData(d.dates.map((date: string, i: number) => ({
            date,
            dayLabel: i === 0 ? "Today" : i === 1 ? "Tomorrow" : new Date(date + "T00:00:00").toLocaleDateString("en-IN", { weekday: "short" }),
            weather_code: d.weather_code?.[i] ?? 0,
            high: d.temperature_max?.[i],
            low: d.temperature_min?.[i],
            rainProb: d.precipitation_probability_max?.[i],
          })));
        }
      } else {
        setError("Failed to load weather data");
      }

      if (monitoringResp.status === "fulfilled") setMonitoring(monitoringResp.value);
      if (healthResp.status === "fulfilled") setSystemHealth(healthResp.value);
    } catch (e: any) {
      setError(e.message || "Failed to load dashboard");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error && !weather) return <ErrorState title="Dashboard Error" message={error} onRetry={fetchData} />;

  const temp = weather?.temperature_2m;
  const feelsLike = weather?.apparent_temperature;
  const humidity = weather?.relative_humidity_2m;
  const windSpeed = weather?.wind_speed_10m;
  const windDir = weather?.wind_direction_10m;
  const pressure = weather?.pressure_msl;
  const cloudCover = weather?.cloud_cover;
  const weatherCode = weather?.weather_code ?? 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Overview"
        description={`Weather intelligence dashboard · ${currentLocation?.name || locationId}`}
        icon={<LayoutDashboard size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
      >
        {systemHealth && (
          <StatusBadge variant={healthBadgeVariant(systemHealth.status)}>{systemHealth.status}</StatusBadge>
        )}
      </PageHeader>

      {/* Row 1: Hero weather + Quick Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Hero Card */}
        <div className="lg:col-span-5 rounded-xl border p-6" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--muted-foreground)" }}>
                Current Conditions
              </p>
              <div className="flex items-end gap-2 mt-2">
                <span className="text-5xl font-bold tracking-tighter" style={{ color: "var(--foreground)" }}>
                  {temp?.toFixed(1) ?? "—"}
                </span>
                <span className="text-2xl font-light mb-1" style={{ color: "var(--muted-foreground)" }}>°C</span>
              </div>
              <p className="text-sm mt-1" style={{ color: "var(--muted-foreground)" }}>
                Feels like {feelsLike?.toFixed(1) ?? "—"}°C
              </p>
              <div className="flex items-center gap-2 mt-3">
                <WeatherIcon code={weatherCode} size={20} />
                <span className="text-sm font-medium" style={{ color: "var(--foreground)" }}>{weatherCondition(weatherCode)}</span>
              </div>
            </div>
            <WeatherIcon code={weatherCode} size={56} />
          </div>
          <Link href="/weather/current" className="flex items-center gap-1 text-xs font-medium mt-4 transition-colors hover:opacity-80" style={{ color: "var(--primary)" }}>
            View full conditions <ArrowRight size={12} />
          </Link>
        </div>

        {/* Quick Metrics */}
        <div className="lg:col-span-7 grid grid-cols-2 md:grid-cols-3 gap-3">
          <QuickMetric icon={<Droplets size={16} />} label="Humidity" value={`${humidity?.toFixed(0) ?? "—"}%`} color="var(--chart-blue)" />
          <QuickMetric icon={<Wind size={16} />} label="Wind" value={`${windSpeed?.toFixed(1) ?? "—"} km/h`} subtext={windDirection(windDir ?? 0)} color="var(--chart-teal)" />
          <QuickMetric icon={<Gauge size={16} />} label="Pressure" value={`${pressure?.toFixed(0) ?? "—"} hPa`} color="var(--chart-amber)" />
          <QuickMetric icon={<Eye size={16} />} label="Cloud Cover" value={`${cloudCover?.toFixed(0) ?? "—"}%`} color="var(--chart-violet)" />
          <QuickMetric icon={<Cpu size={16} />} label="Champions" value={monitoring?.champion_models?.toString() ?? systemHealth?.champion_count?.toString() ?? "—"} color="var(--success)" />
          <QuickMetric icon={<BarChart3 size={16} />} label="Predictions (24h)" value={monitoring?.prediction_volume_24h?.toLocaleString() ?? "—"} color="var(--primary)" />
        </div>
      </div>

      {/* Row 2: Hourly Temperature + Rain Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {hourlyChart.length > 0 && (
          <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>24h Temperature Forecast</h3>
              <Link href="/weather/hourly" className="text-[11px] font-medium" style={{ color: "var(--primary)" }}>View All →</Link>
            </div>
            <ResponsiveContainer width="100%" height={chartHeight("sm")}>
              <AreaChart data={hourlyChart} margin={CHART_MARGIN}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--chart-text)" }} />
                <YAxis tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="°" />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Area type="monotone" dataKey="temperature" stroke={SERIES_COLORS.temperature} fill={SERIES_COLORS.temperature} fillOpacity={0.1} name="Temp (°C)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
        {hourlyChart.length > 0 && (
          <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>Rain Probability & Precipitation</h3>
              <Link href="/forecast/rainfall" className="text-[11px] font-medium" style={{ color: "var(--primary)" }}>AI Forecast →</Link>
            </div>
            <ResponsiveContainer width="100%" height={chartHeight("sm")}>
              <ComposedChart data={hourlyChart} margin={CHART_MARGIN}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--chart-text)" }} />
                <YAxis yAxisId="prob" tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="%" domain={[0, 100]} />
                <YAxis yAxisId="mm" orientation="right" tick={{ fontSize: 11, fill: "var(--chart-text)" }} unit="mm" />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Line yAxisId="prob" type="monotone" dataKey="rainProb" stroke={SERIES_COLORS.rainProbability} name="Probability (%)" strokeWidth={2} dot={false} />
                <Bar yAxisId="mm" dataKey="precipitation" fill={SERIES_COLORS.rainfall} name="Rainfall (mm)" radius={[2, 2, 0, 0]} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Row 3: Daily Forecast Strip */}
      {dailyData.length > 0 && (
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>7-Day Forecast</h3>
            <Link href="/weather/daily" className="text-[11px] font-medium" style={{ color: "var(--primary)" }}>Details →</Link>
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-7 gap-3">
            {dailyData.slice(0, 7).map((day, i) => (
              <div key={i} className="flex flex-col items-center gap-1 py-3 rounded-lg text-center"
                   style={{ background: i === 0 ? "var(--primary-muted)" : "transparent" }}>
                <span className="text-[11px] font-semibold" style={{ color: i === 0 ? "var(--primary)" : "var(--muted-foreground)" }}>{day.dayLabel}</span>
                <WeatherIcon code={day.weather_code} size={24} />
                <div className="flex items-center gap-1 text-xs">
                  <span className="font-semibold" style={{ color: "var(--chart-rose)" }}>{day.high?.toFixed(0)}°</span>
                  <span style={{ color: "var(--muted-foreground)" }}>/</span>
                  <span style={{ color: "var(--chart-blue)" }}>{day.low?.toFixed(0)}°</span>
                </div>
                <span className="text-[10px]" style={{ color: "var(--chart-cyan)" }}>{day.rainProb?.toFixed(0) ?? "—"}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Row 4: ML Intelligence Summary + System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* ML Summary */}
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>ML Intelligence</h3>
            <Link href="/ml/performance" className="text-[11px] font-medium" style={{ color: "var(--primary)" }}>View All →</Link>
          </div>
          <div className="space-y-3">
            {monitoring && (
              <>
                <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: "var(--border-subtle)" }}>
                  <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Champion Models</span>
                  <span className="text-sm font-bold" style={{ color: "var(--success)" }}>{monitoring.champion_models ?? systemHealth?.champion_count ?? 0}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: "var(--border-subtle)" }}>
                  <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Total Models</span>
                  <span className="text-sm font-bold" style={{ color: "var(--foreground)" }}>{monitoring.total_models ?? systemHealth?.model_count ?? 0}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b" style={{ borderColor: "var(--border-subtle)" }}>
                  <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Predictions (7d)</span>
                  <span className="text-sm font-bold" style={{ color: "var(--primary)" }}>{monitoring.prediction_volume_7d?.toLocaleString() ?? "—"}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-xs" style={{ color: "var(--muted-foreground)" }}>Drift Events (30d)</span>
                  <span className="text-sm font-bold" style={{ color: monitoring.drift_events_30d > 0 ? "var(--warning)" : "var(--success)" }}>
                    {monitoring.drift_events_30d ?? 0}
                  </span>
                </div>
              </>
            )}
            {!monitoring && (
              <p className="text-sm text-center py-4" style={{ color: "var(--muted-foreground)" }}>
                ML monitoring data unavailable
              </p>
            )}
          </div>
        </div>

        {/* System Health */}
        <div className="rounded-xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>System Status</h3>
            <Link href="/system/health" className="text-[11px] font-medium" style={{ color: "var(--primary)" }}>Details →</Link>
          </div>
          {systemHealth?.services ? (
            <div className="space-y-2.5">
              {systemHealth.services.map((svc: any) => (
                <div key={svc.name} className="flex items-center justify-between py-1.5">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full shrink-0"
                          style={{ background: svc.status === "healthy" ? "var(--success)" : svc.status === "degraded" ? "var(--warning)" : "var(--danger)" }} />
                    <span className="text-xs font-medium" style={{ color: "var(--foreground)" }}>{svc.name}</span>
                  </div>
                  <StatusBadge variant={healthBadgeVariant(svc.status)} dot={false}>{svc.status}</StatusBadge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-center py-4" style={{ color: "var(--muted-foreground)" }}>
              System health data unavailable
            </p>
          )}
        </div>
      </div>

      {/* Quick Navigation */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "AI Temperature", href: "/forecast/temperature", icon: <Thermometer size={16} />, color: "var(--chart-orange)" },
          { label: "AI Rainfall", href: "/forecast/rainfall", icon: <Droplets size={16} />, color: "var(--chart-blue)" },
          { label: "AI Wind", href: "/forecast/wind", icon: <Wind size={16} />, color: "var(--chart-teal)" },
          { label: "Forecast Verification", href: "/ml/verification", icon: <TrendingUp size={16} />, color: "var(--chart-emerald)" },
        ].map((nav) => (
          <Link key={nav.href} href={nav.href}
            className="flex items-center gap-3 rounded-xl border p-4 transition-all hover:shadow-md group"
            style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <div className="p-2 rounded-lg transition-transform group-hover:scale-110" style={{ background: `${nav.color}15`, color: nav.color }}>
              {nav.icon}
            </div>
            <div>
              <p className="text-xs font-semibold" style={{ color: "var(--foreground)" }}>{nav.label}</p>
              <p className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>View →</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

function QuickMetric({ icon, label, value, subtext, color }: {
  icon: React.ReactNode; label: string; value: string; subtext?: string; color: string;
}) {
  return (
    <div className="rounded-xl border p-3.5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
      <div className="flex items-center gap-2 mb-1.5">
        <span style={{ color }}>{icon}</span>
        <span className="text-[11px] font-medium" style={{ color: "var(--muted-foreground)" }}>{label}</span>
      </div>
      <p className="text-lg font-bold" style={{ color: "var(--foreground)" }}>{value}</p>
      {subtext && <p className="text-[10px] mt-0.5" style={{ color: "var(--muted-foreground)" }}>{subtext}</p>}
    </div>
  );
}
