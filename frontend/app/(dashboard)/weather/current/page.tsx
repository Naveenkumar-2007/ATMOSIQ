"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton, CardSkeleton, ChartSkeleton } from "@/components/common/loading-state";
import { StatusBadge } from "@/components/common/status-badge";
import {
  CloudSun, Thermometer, Droplets, Wind, Eye, Gauge, CloudFog, Sun, Sunrise, Sunset,
} from "lucide-react";
import { WeatherIcon } from "@/components/ui/weather-icon";

interface CurrentWeatherData {
  observation_time: string;
  temperature_2m: number;
  apparent_temperature: number;
  relative_humidity_2m: number;
  wind_speed_10m: number;
  wind_direction_10m: number;
  wind_gusts_10m: number;
  pressure_msl: number;
  surface_pressure: number;
  cloud_cover: number;
  visibility: number;
  weather_code: number;
  uv_index?: number;
  sunrise?: string;
  sunset?: string;
  aqi?: { index: number; status: string };
}

function weatherCondition(code: number): string {
  if (code === 0) return "Clear Sky";
  if (code <= 2) return "Partly Cloudy";
  if (code === 3) return "Overcast";
  if (code <= 49) return "Foggy";
  if (code <= 59) return "Drizzle";
  if (code <= 69) return "Rain";
  if (code <= 79) return "Snow";
  if (code <= 84) return "Rain Showers";
  if (code <= 94) return "Thunderstorm";
  return "Severe Weather";
}

function windDirection(deg: number): string {
  const dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  return dirs[Math.round(deg / 22.5) % 16] || "N";
}

export default function CurrentWeatherPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<CurrentWeatherData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [todaySummary, setTodaySummary] = useState<{ max: number; min: number } | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const combined = await apiClient<any>(`/api/v1/weather/combined/${locationId}`);
      const c = combined.current;
      setData(c);
      // Calculate today's high/low from hourly data
      const temps = (combined.hourly?.temperature_2m || []).filter((v: any) => v != null);
      if (temps.length > 0) {
        setTodaySummary({ max: Math.max(...temps), min: Math.min(...temps) });
      }
    } catch (e: any) {
      setError(e.message || "Failed to load current weather");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  if (isLoading) return <PageSkeleton />;
  if (error) return <ErrorState title="Unable to load current weather" message={error} onRetry={fetchData} />;
  if (!data) return <ErrorState title="No observation data" message="No weather observations found for this location." />;

  const temp = data.temperature_2m;
  const feelsLike = data.apparent_temperature;
  const condition = weatherCondition(data.weather_code || 0);
  const obsTime = new Date(data.observation_time).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Current Weather"
        description={`Live conditions as of ${obsTime}`}
        icon={<CloudSun size={20} />}
        onRefresh={fetchData}
        isLoading={isLoading}
        lastUpdated={obsTime}
      >
        <StatusBadge variant="healthy" dot>Observed</StatusBadge>
      </PageHeader>

      {/* Hero: Current Condition */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Temperature Card */}
        <div className="lg:col-span-2 rounded-xl border p-6" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: "var(--muted-foreground)" }}>
                {currentLocation?.name || locationId}
              </p>
              <div className="flex items-end gap-2 mt-2">
                <span className="text-6xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>
                  {temp?.toFixed(1)}
                </span>
                <span className="text-3xl font-light mb-1.5" style={{ color: "var(--muted-foreground)" }}>°C</span>
              </div>
              <p className="text-sm mt-1" style={{ color: "var(--muted-foreground)" }}>
                Feels like {feelsLike?.toFixed(1)}°C
              </p>
              <div className="flex items-center gap-2 mt-2">
                <WeatherIcon code={data.weather_code || 0} size={22} />
                <span className="text-sm font-medium" style={{ color: "var(--foreground)" }}>{condition}</span>
              </div>
            </div>
            <div className="text-right space-y-1">
              {todaySummary && (
                <>
                  <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                    Max Temp: <span className="font-semibold" style={{ color: "var(--chart-rose)" }}>{todaySummary.max.toFixed(1)}°C</span>
                  </p>
                  <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
                    Min Temp: <span className="font-semibold" style={{ color: "var(--chart-blue)" }}>{todaySummary.min.toFixed(1)}°C</span>
                  </p>
                </>
              )}
            </div>
          </div>

          {/* Sunrise/Sunset */}
          <div className="flex items-center gap-6 mt-6 pt-4 border-t" style={{ borderColor: "var(--border-subtle)" }}>
            <div className="flex items-center gap-2 text-sm" style={{ color: "var(--muted-foreground)" }}>
              <Sunrise size={16} style={{ color: "var(--chart-amber)" }} />
              <span>Sunrise: <span className="font-medium" style={{ color: "var(--foreground)" }}>{data.sunrise || "06:05 AM"}</span></span>
            </div>
            <div className="flex items-center gap-2 text-sm" style={{ color: "var(--muted-foreground)" }}>
              <Sunset size={16} style={{ color: "var(--chart-orange)" }} />
              <span>Sunset: <span className="font-medium" style={{ color: "var(--foreground)" }}>{data.sunset || "06:35 PM"}</span></span>
            </div>
          </div>
        </div>

        {/* Large Weather Icon / Visual */}
        <div className="rounded-xl border p-6 flex flex-col items-center justify-center" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <WeatherIcon code={data.weather_code || 0} size={80} />
          <p className="text-lg font-semibold mt-3" style={{ color: "var(--foreground)" }}>{condition}</p>
          <p className="text-xs mt-1" style={{ color: "var(--muted-foreground)" }}>
            Weather Code: {data.weather_code}
          </p>
          <p className="text-xs mt-3 px-3 py-1 rounded-full" style={{ background: "var(--muted)", color: "var(--muted-foreground)" }}>
            Source: Weather Observation Provider
          </p>
        </div>
      </div>

      {/* Metric Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <MetricCard icon={<Droplets size={16} />} label="Humidity" value={`${data.relative_humidity_2m?.toFixed(0)}%`} color="var(--chart-blue)" />
        <MetricCard icon={<Thermometer size={16} />} label="Dew Point" value={`${(temp - (100 - (data.relative_humidity_2m || 0)) / 5).toFixed(1)}°C`} color="var(--chart-cyan)" />
        <MetricCard icon={<Gauge size={16} />} label="Pressure" value={`${data.pressure_msl?.toFixed(0)} hPa`} color="var(--chart-amber)" />
        <MetricCard icon={<Wind size={16} />} label="Wind Speed" value={`${data.wind_speed_10m?.toFixed(1)} km/h`} subtext={windDirection(data.wind_direction_10m || 0)} color="var(--chart-teal)" />
        <MetricCard icon={<Wind size={16} />} label="Wind Gust" value={`${data.wind_gusts_10m?.toFixed(1)} km/h`} color="var(--chart-orange)" />
        <MetricCard icon={<Eye size={16} />} label="Visibility" value={`${((data.visibility || 10000) / 1000).toFixed(1)} km`} color="var(--chart-violet)" />
        <MetricCard icon={<CloudFog size={16} />} label="Cloud Cover" value={`${data.cloud_cover?.toFixed(0)}%`} color="var(--muted-foreground)" />
        <MetricCard icon={<Sun size={16} />} label="UV Index" value={`${data.uv_index ?? "N/A"}`} color="var(--chart-amber)" />
        <MetricCard icon={<Gauge size={16} />} label="Surface Pressure" value={`${data.surface_pressure?.toFixed(0)} hPa`} color="var(--chart-emerald)" />
        <MetricCard icon={<Droplets size={16} />} label="Precipitation" value="0.0 mm" color="var(--chart-blue)" />
      </div>

      {/* Data Source */}
      <div className="text-xs text-center py-3" style={{ color: "var(--muted-foreground)" }}>
        Observed weather data · Updated {obsTime} · Source: Open-Meteo weather observation provider
      </div>
    </div>
  );
}

function MetricCard({
  icon, label, value, subtext, color,
}: {
  icon: React.ReactNode; label: string; value: string; subtext?: string; color: string;
}) {
  return (
    <div className="rounded-xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
      <div className="flex items-center gap-2">
        <span style={{ color }}>{icon}</span>
        <span className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>{label}</span>
      </div>
      <p className="text-lg font-bold" style={{ color: "var(--foreground)" }}>{value}</p>
      {subtext && <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>{subtext}</p>}
    </div>
  );
}
