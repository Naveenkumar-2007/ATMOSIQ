import React from "react";
import { Card } from "@/components/ui/card";
import { WeatherIcon } from "@/components/ui/weather-icon";
import { DailyForecastItem } from "@/types/weather";

interface DailyForecastStripProps {
  days: DailyForecastItem[];
}

export function DailyForecastStrip({ days }: DailyForecastStripProps) {
  return (
    <Card className="p-5 bg-slate-900 border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-100">7-Day Synoptic Weather Outlook</h3>
          <p className="text-xs text-slate-400 mt-0.5">Aggregated multi-model ensemble forecast</p>
        </div>
        <span className="text-xs text-sky-400 font-medium bg-sky-500/10 px-2.5 py-0.5 rounded-full border border-sky-500/20">
          7 Days
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {days.map((day, idx) => (
          <div
            key={idx}
            className="flex flex-col items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-sky-500/40 hover:bg-slate-800/40 transition-all text-center group"
          >
            <span className="text-xs font-semibold text-slate-300 group-hover:text-sky-400 transition-colors">
              {day.dayName}
            </span>

            <div className="my-2.5 p-2 rounded-lg bg-slate-900/80 group-hover:scale-110 transition-transform">
              <WeatherIcon code={day.weatherCode} size={28} />
            </div>

            <div className="flex items-baseline gap-1 text-xs">
              <span className="font-bold text-slate-100">{Math.round(day.tempMax)}°</span>
              <span className="text-slate-400 text-[11px]">/ {Math.round(day.tempMin)}°</span>
            </div>

            <div className="mt-2 text-[11px] flex items-center gap-1 text-sky-400 font-medium">
              <span>💧 {day.precipitationProbabilityMax}%</span>
            </div>
            {day.precipitationSum > 0 && (
              <span className="text-[10px] text-slate-400 mt-0.5">{day.precipitationSum.toFixed(1)} mm</span>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}
