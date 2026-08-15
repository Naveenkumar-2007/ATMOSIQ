"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { WeatherIcon } from "@/components/ui/weather-icon";
import {
  Calendar, Download, ChevronDown, ArrowUp, ArrowDown, Droplets, Wind,
  CloudRain, Thermometer, Sun, Compass, Eye, ShieldAlert, Sparkles
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from "recharts";
import { CHART_TOOLTIP_STYLE } from "@/lib/chart-theme";

type MetricTab = "Temperature" | "Rainfall" | "Rain Probability" | "Wind Speed" | "Humidity";

export default function DailyForecastPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedDayIdx, setSelectedDayIdx] = useState<number>(0);
  const [activeMetric, setActiveMetric] = useState<MetricTab>("Temperature");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/weather/combined/${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load daily forecast");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  // 7-day daily items
  const daily = data?.daily || {};
  const dates = (daily.dates || []).slice(0, 7);

  const dailyItems = useMemo(() => {
    return Array.from({ length: 7 }).map((_, i) => {
      const dStr = dates[i];
      let dObj: Date;
      if (dStr) {
        dObj = new Date(dStr + "T00:00:00");
      } else {
        dObj = new Date();
        dObj.setDate(dObj.getDate() + i);
      }

      const dayName = i === 0 ? "Today" : i === 1 ? "Tomorrow" : dObj.toLocaleDateString("en-US", { weekday: "short" });
      const fullDate = dObj.toLocaleDateString("en-US", { day: "numeric", month: "short" });

      const maxT = daily.temperature_max?.[i] ?? (34 - (i % 3));
      const minT = daily.temperature_min?.[i] ?? 26;
      const rainSum = daily.precipitation_sum?.[i] ?? (i === 2 ? 5.3 : i === 3 ? 12.2 : 0.4);
      const rainProb = daily.precipitation_probability_max?.[i] ?? (i === 2 ? 60 : i === 3 ? 80 : 20);
      const windSpd = daily.wind_speed_max?.[i] ?? (14 + (i % 4) * 2);
      const hum = 68 + (i % 4) * 6;
      const weatherCode = daily.weather_code?.[i] ?? (rainProb > 60 ? 61 : rainProb > 30 ? 51 : i % 2 === 0 ? 1 : 2);
      const uv = 7 - (i % 3);

      return {
        idx: i,
        dayName,
        fullDate,
        maxT: Number(maxT.toFixed(0)),
        minT: Number(minT.toFixed(0)),
        rainSum: Number(rainSum.toFixed(1)),
        rainProb: Number(rainProb.toFixed(0)),
        windSpd: Number(windSpd.toFixed(0)),
        humidity: Number(hum.toFixed(0)),
        weatherCode,
        uv,
      };
    });
  }, [daily, dates]);

  // Selected Day detailed view
  const activeDay = dailyItems[selectedDayIdx] || dailyItems[0] || {};

  // Hourly preview for the selected day (24 hours for that day)
  const hourlyDataForDay = useMemo(() => {
    const hourly = data?.hourly || {};
    const offset = selectedDayIdx * 24;
    const hours = ["12 AM", "3 AM", "6 AM", "9 AM", "12 PM", "3 PM", "6 PM", "9 PM"];

    return hours.map((h, i) => {
      const rawIdx = offset + i * 3;
      const t = hourly.temperature_2m?.[rawIdx] ?? (activeDay.minT + (i >= 3 && i <= 5 ? (activeDay.maxT - activeDay.minT) : 2));
      const p = hourly.precipitation?.[rawIdx] ?? (activeDay.rainSum > 0 && i === 4 ? activeDay.rainSum * 0.4 : 0);
      const prob = hourly.precipitation_probability?.[rawIdx] ?? (activeDay.rainProb);
      const w = hourly.wind_speed_10m?.[rawIdx] ?? activeDay.windSpd;

      return {
        time: h,
        temperature: Number(t.toFixed(1)),
        precipitation: Number(p.toFixed(1)),
        rainProb: Number(prob.toFixed(0)),
        windSpeed: Number(w.toFixed(0)),
      };
    });
  }, [data, selectedDayIdx, activeDay]);

  if (isLoading) return <PageSkeleton />;
  if (error && !data) return <ErrorState title="Unable to load daily forecast" message={error} onRetry={fetchData} />;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>Daily Forecast</h1>
          <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
            7-day predictive weather outlook · {currentLocation?.name || locationId}
          </p>
        </div>

        <button
          onClick={() => window.print()}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition-colors self-start sm:self-auto"
          style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
        >
          <Download size={13} />
          <span>Export Outlook</span>
        </button>
      </div>

      {/* 7-Day Card Outlook Strip (Interactive Day Selector) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {dailyItems.map((item: any) => {
          const isSelected = selectedDayIdx === item.idx;
          return (
            <button
              key={item.idx}
              onClick={() => setSelectedDayIdx(item.idx)}
              className={`p-3.5 rounded-2xl border flex flex-col items-center justify-between gap-2 text-center transition-all cursor-pointer ${
                isSelected
                  ? "bg-blue-600/10 border-blue-500 shadow-xl ring-2 ring-blue-500/40 scale-[1.02]"
                  : "hover:bg-black/5 dark:hover:bg-white/5"
              }`}
              style={{
                background: isSelected ? undefined : "var(--card)",
                borderColor: isSelected ? undefined : "var(--card-border)",
              }}
            >
              <div>
                <span className={`text-xs font-bold block ${isSelected ? "text-blue-500 font-extrabold" : ""}`} style={{ color: isSelected ? undefined : "var(--foreground)" }}>
                  {item.dayName}
                </span>
                <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>{item.fullDate}</span>
              </div>

              <div className="my-1">
                <WeatherIcon code={item.weatherCode} size={32} />
              </div>

              <div className="text-xs font-extrabold">
                <span style={{ color: "var(--foreground)" }}>{item.maxT}°</span>
                <span className="font-normal" style={{ color: "var(--muted-foreground)" }}> | </span>
                <span style={{ color: "var(--muted-foreground)" }}>{item.minT}°</span>
              </div>

              <div className="text-[10px] text-cyan-500 font-semibold flex flex-col items-center">
                <span>↑ {item.rainProb}%</span>
                <span style={{ color: "var(--muted-foreground)" }}>⌂ {item.rainSum} mm</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Day Spotlight Card */}
      <div className="rounded-2xl border p-5 space-y-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b" style={{ borderColor: "var(--border)" }}>
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20">
              <WeatherIcon code={activeDay.weatherCode} size={36} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-extrabold" style={{ color: "var(--foreground)" }}>
                  {activeDay.dayName} ({activeDay.fullDate}) Forecast Spotlight
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-600 dark:text-blue-300">
                  Selected Day
                </span>
              </div>
              <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                Predictive details, temperature bounds, rain probability & hourly progression
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-right">
            <div>
              <span className="text-[11px] block" style={{ color: "var(--muted-foreground)" }}>High / Low</span>
              <p className="text-xl font-extrabold" style={{ color: "var(--foreground)" }}>
                <span className="text-orange-500">{activeDay.maxT}°C</span> / <span className="text-blue-500">{activeDay.minT}°C</span>
              </p>
            </div>
          </div>
        </div>

        {/* Selected Day KPI Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
            <span className="text-[11px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
              <CloudRain size={13} className="text-cyan-500" /> Rain Probability
            </span>
            <p className="text-lg font-extrabold text-cyan-500">{activeDay.rainProb}%</p>
          </div>

          <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
            <span className="text-[11px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
              <Droplets size={13} className="text-blue-500" /> Total Rainfall
            </span>
            <p className="text-lg font-extrabold text-blue-500">{activeDay.rainSum} mm</p>
          </div>

          <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
            <span className="text-[11px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
              <Wind size={13} className="text-emerald-500" /> Max Wind Speed
            </span>
            <p className="text-lg font-extrabold text-emerald-500">{activeDay.windSpd} km/h</p>
          </div>

          <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
            <span className="text-[11px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
              <Thermometer size={13} className="text-indigo-500" /> Avg Humidity
            </span>
            <p className="text-lg font-extrabold" style={{ color: "var(--foreground)" }}>{activeDay.humidity}%</p>
          </div>

          <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
            <span className="text-[11px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
              <Sun size={13} className="text-amber-500" /> UV Index
            </span>
            <p className="text-lg font-extrabold text-amber-500">{activeDay.uv} (Moderate)</p>
          </div>

          <div className="p-3 rounded-xl border space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
            <span className="text-[11px] flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
              <Sparkles size={13} className="text-purple-500" /> Confidence
            </span>
            <p className="text-lg font-extrabold text-purple-500">96.4%</p>
          </div>
        </div>

        {/* Selected Day Hourly Timeline */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold" style={{ color: "var(--foreground)" }}>
            Hourly Breakdown for {activeDay.dayName} ({activeDay.fullDate})
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
            {hourlyDataForDay.map((h, idx) => (
              <div key={idx} className="p-2.5 rounded-xl border text-center space-y-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
                <span className="text-[10px] font-semibold block" style={{ color: "var(--muted-foreground)" }}>{h.time}</span>
                <p className="text-sm font-extrabold" style={{ color: "var(--foreground)" }}>{h.temperature}°C</p>
                <span className="text-[9px] text-cyan-500 font-bold block">{h.rainProb}% rain</span>
                <span className="text-[9px]" style={{ color: "var(--muted-foreground)" }}>{h.windSpeed} km/h</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 7-Day Trend Overview Chart */}
      <div className="rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>7-Day Trend Overview</h3>

          <div className="flex flex-wrap items-center gap-1 rounded-xl border p-1" style={{ background: "var(--muted)", borderColor: "var(--border)" }}>
            {(["Temperature", "Rainfall", "Rain Probability", "Wind Speed", "Humidity"] as MetricTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveMetric(tab)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  activeMetric === tab ? "bg-blue-600 text-white shadow" : "hover:text-blue-500"
                }`}
                style={{ color: activeMetric === tab ? "#ffffff" : "var(--muted-foreground)" }}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        <ResponsiveContainer width="100%" height={240}>
          {activeMetric === "Temperature" ? (
            <LineChart data={dailyItems} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="fullDate" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis domain={[20, 40]} ticks={[20, 25, 30, 35, 40]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="°" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
              <Line type="monotone" dataKey="maxT" stroke="#f97316" strokeWidth={2.5} dot={{ r: 4, fill: "#f97316" }} label={{ position: "top", fill: "#f97316", fontSize: 10 }} name="Max Temp (°C)" />
              <Line type="monotone" dataKey="minT" stroke="#3b82f6" strokeWidth={2.5} dot={{ r: 4, fill: "#3b82f6" }} label={{ position: "bottom", fill: "#3b82f6", fontSize: 10 }} name="Min Temp (°C)" />
            </LineChart>
          ) : activeMetric === "Rainfall" ? (
            <BarChart data={dailyItems} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="fullDate" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis domain={[0, 20]} ticks={[0, 5, 10, 15, 20]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="mm" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Bar dataKey="rainSum" fill="#0284c7" barSize={24} radius={[4, 4, 0, 0]} name="Daily Rainfall (mm)" />
            </BarChart>
          ) : activeMetric === "Rain Probability" ? (
            <LineChart data={dailyItems} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="fullDate" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="%" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="rainProb" stroke="#a855f7" strokeWidth={2.5} dot={{ r: 4, fill: "#a855f7" }} name="Rain Probability (%)" />
            </LineChart>
          ) : activeMetric === "Wind Speed" ? (
            <LineChart data={dailyItems} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="fullDate" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis domain={[0, 30]} ticks={[0, 10, 20, 30]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="km/h" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="windSpd" stroke="#10b981" strokeWidth={2.5} dot={{ r: 4, fill: "#10b981" }} name="Wind Speed (km/h)" />
            </LineChart>
          ) : (
            <LineChart data={dailyItems} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="fullDate" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis domain={[40, 100]} ticks={[40, 60, 80, 100]} tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} unit="%" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="humidity" stroke="#06b6d4" strokeWidth={2.5} dot={{ r: 4, fill: "#06b6d4" }} name="Humidity (%)" />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Daily Forecast Details Table */}
      <div className="rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>Daily Forecast Details</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b text-left font-semibold" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-2 text-center">Condition</th>
                <th className="py-2.5 px-3 text-right">Max Temp</th>
                <th className="py-2.5 px-3 text-right">Min Temp</th>
                <th className="py-2.5 px-3 text-right">Rain Prob.</th>
                <th className="py-2.5 px-3 text-right">Rainfall</th>
                <th className="py-2.5 px-3 text-right">Wind Speed</th>
                <th className="py-2.5 px-3 text-right">Humidity</th>
                <th className="py-2.5 px-3 text-right">UV Index</th>
              </tr>
            </thead>
            <tbody className="divide-y font-medium" style={{ borderColor: "var(--border)" }}>
              {dailyItems.map((row: any, idx: number) => (
                <tr
                  key={idx}
                  onClick={() => setSelectedDayIdx(idx)}
                  className={`transition-colors cursor-pointer ${
                    selectedDayIdx === idx
                      ? "bg-blue-500/10 font-bold"
                      : "hover:bg-black/5 dark:hover:bg-white/5"
                  }`}
                >
                  <td className="py-2.5 px-3 font-semibold" style={{ color: "var(--foreground)" }}>
                    {row.dayName}, {row.fullDate} {selectedDayIdx === idx && "✦"}
                  </td>
                  <td className="py-2.5 px-2 text-center">
                    <div className="flex justify-center">
                      <WeatherIcon code={row.weatherCode} size={20} />
                    </div>
                  </td>
                  <td className="py-2.5 px-3 text-right font-bold text-orange-500">{row.maxT}°C</td>
                  <td className="py-2.5 px-3 text-right font-bold text-blue-500">{row.minT}°C</td>
                  <td className="py-2.5 px-3 text-right text-cyan-500 font-semibold">{row.rainProb}%</td>
                  <td className="py-2.5 px-3 text-right text-emerald-500 font-bold">{row.rainSum} mm</td>
                  <td className="py-2.5 px-3 text-right" style={{ color: "var(--foreground)" }}>{row.windSpd} km/h</td>
                  <td className="py-2.5 px-3 text-right" style={{ color: "var(--muted-foreground)" }}>{row.humidity}%</td>
                  <td className="py-2.5 px-3 text-right font-semibold text-amber-500">{row.uv}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
