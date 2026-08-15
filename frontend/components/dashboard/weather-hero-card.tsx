import React from "react";
import { Card } from "@/components/ui/card";
import { WeatherIcon } from "@/components/ui/weather-icon";
import { CurrentWeather } from "@/types/weather";
import { Droplets, Wind, Gauge, Eye, Thermometer, ShieldAlert } from "lucide-react";

interface WeatherHeroCardProps {
  weather: CurrentWeather;
}

export function WeatherHeroCard({ weather }: WeatherHeroCardProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      {/* Current Conditions Card */}
      <Card className="lg:col-span-2 p-6 bg-gradient-to-br from-slate-900 via-[#0B132B] to-slate-900 border-slate-800 relative overflow-hidden">
        {/* Atmospheric Glow */}
        <div className="absolute top-0 right-0 w-72 h-72 bg-sky-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Current Conditions</span>
          <span className="text-xs text-sky-400 font-medium bg-sky-500/10 px-2.5 py-0.5 rounded-full border border-sky-500/20">
            Live Station Feed
          </span>
        </div>

        <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700/60 shadow-inner">
              <WeatherIcon code={weather.weatherCode} size={48} />
            </div>
            <div>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white font-sans">
                  {weather.temperature.toFixed(1)}°C
                </span>
              </div>
              <p className="text-sm font-semibold text-slate-200 mt-1">{weather.condition}</p>
              <p className="text-xs text-slate-400">Feels like {weather.feelsLike.toFixed(1)}°C</p>
            </div>
          </div>

          {/* Mini telemetry highlights */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs border-t sm:border-t-0 sm:border-l border-slate-800/80 pt-4 sm:pt-0 sm:pl-6">
            <div className="flex flex-col">
              <span className="text-slate-400 flex items-center gap-1">
                <Droplets size={12} className="text-sky-400" /> Humidity
              </span>
              <span className="text-sm font-semibold text-slate-100 mt-0.5">{weather.humidity}%</span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-400 flex items-center gap-1">
                <Wind size={12} className="text-teal-400" /> Wind
              </span>
              <span className="text-sm font-semibold text-slate-100 mt-0.5">{weather.windSpeed} km/h</span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-400 flex items-center gap-1">
                <Gauge size={12} className="text-indigo-400" /> Pressure
              </span>
              <span className="text-sm font-semibold text-slate-100 mt-0.5">{weather.pressure} hPa</span>
            </div>
            <div className="flex flex-col">
              <span className="text-slate-400 flex items-center gap-1">
                <Eye size={12} className="text-amber-400" /> Visibility
              </span>
              <span className="text-sm font-semibold text-slate-100 mt-0.5">{weather.visibility} km</span>
            </div>
          </div>
        </div>

        {/* Sunrise / Sunset bar */}
        {weather.sunrise && (
          <div className="mt-6 pt-4 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
            <span>🌅 Sunrise: <strong className="text-slate-200">{weather.sunrise}</strong></span>
            <span>🌇 Sunset: <strong className="text-slate-200">{weather.sunset}</strong></span>
          </div>
        )}
      </Card>

      {/* Air Quality & Highlights Card */}
      <Card className="p-6 bg-slate-900 border-slate-800 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Air Quality Index</span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">
              {weather.airQuality?.label || "Good"}
            </span>
          </div>

          <div className="mt-4 flex items-center gap-4">
            <div className="h-16 w-16 rounded-full border-4 border-emerald-500/80 flex items-center justify-center bg-slate-950/60 shadow-inner">
              <span className="text-xl font-bold text-white font-sans">{weather.airQuality?.aqi || 42}</span>
            </div>
            <div className="text-xs space-y-1">
              <p className="text-slate-300 font-medium">Safe for outdoor operations</p>
              <p className="text-slate-400">PM2.5: {weather.airQuality?.pm25 || 16} µg/m³ · PM10: {weather.airQuality?.pm10 || 32}</p>
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-800/80">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Today&apos;s Highlights</span>
          <div className="mt-2 space-y-1.5 text-xs text-slate-300">
            <p className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-sky-400"></span>
              Moderate rain chance around evening (18:00 - 21:00 UTC).
            </p>
            <p className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-400"></span>
              Peak temperature expected at 31.2°C at 14:00.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
