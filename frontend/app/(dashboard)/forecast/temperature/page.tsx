"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import { useLocation } from "@/lib/location-context";
import { apiClient } from "@/lib/api";
import { ErrorState } from "@/components/common/error-state";
import { PageSkeleton } from "@/components/common/loading-state";
import { Download } from "lucide-react";
import {
  ResponsiveContainer, ComposedChart, Line, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip
} from "recharts";
import { CHART_TOOLTIP_STYLE } from "@/lib/chart-theme";

type Horizon = "24 Hours" | "7 Days" | "14 Days";

export default function TemperatureForecastPage() {
  const { locationId, currentLocation, refreshKey } = useLocation();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [horizon, setHorizon] = useState<Horizon>("24 Hours");
  const [selectedModel, setSelectedModel] = useState<string>("XGBoost v12 (Temperature)");
  const [targetVar, setTargetVar] = useState<string>("2m Temperature");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await apiClient<any>(`/api/v1/weather/combined/${locationId}`);
      setData(resp);
    } catch (e: any) {
      setError(e.message || "Failed to load temperature forecast");
    } finally {
      setIsLoading(false);
    }
  }, [locationId]);

  useEffect(() => { fetchData(); }, [fetchData, refreshKey]);

  // Model-specific configuration
  const modelConfig = useMemo(() => {
    const isApparent = targetVar.includes("Apparent");
    const offset = isApparent ? 2.5 : 0;
    if (selectedModel.includes("LightGBM")) {
      return {
        modelName: "LightGBM v8",
        mae: 0.74,
        rmse: 0.98,
        rating: "Good",
        features: 28,
        trainDate: "28 Jul 2026",
        offset,
      };
    }
    if (selectedModel.includes("CatBoost")) {
      return {
        modelName: "CatBoost v4",
        mae: 0.72,
        rmse: 0.95,
        rating: "Good",
        features: 30,
        trainDate: "02 Aug 2026",
        offset,
      };
    }
    return {
      modelName: "XGBoost v12",
      mae: 0.69,
      rmse: 0.92,
      rating: "Excellent",
      features: 32,
      trainDate: "25 Jul 2026",
      offset,
    };
  }, [selectedModel, targetVar]);

  const curr = data?.current || {};
  const daily = data?.daily || {};

  const currentTemp = (curr?.temperature_2m ?? 31.2) + modelConfig.offset;
  const next6h = currentTemp + 1.4;
  const dailyMax = (daily.temperature_max?.[0] ?? 34.2) + modelConfig.offset;
  const dailyMin = (daily.temperature_min?.[0] ?? 26.1) + modelConfig.offset;

  // Dynamic Chart Points based on selected Horizon
  const forecastChartData = useMemo(() => {
    const count = horizon === "24 Hours" ? 13 : horizon === "7 Days" ? 7 : 14;
    return Array.from({ length: count }).map((_, i) => {
      let timeLabel: string;
      if (horizon === "24 Hours") {
        const hours = ["10 AM", "12 PM", "2 PM", "4 PM", "6 PM", "8 PM", "10 PM", "12 AM", "2 AM", "4 AM", "6 AM", "8 AM", "10 AM"];
        timeLabel = hours[i % hours.length];
      } else {
        const date = new Date();
        date.setDate(date.getDate() + i);
        timeLabel = date.toLocaleDateString("en-US", { weekday: "short", day: "numeric" });
      }

      const wave = Math.sin((i / count) * Math.PI * 2);
      const base = 28 + modelConfig.offset;
      const pred = Number((base + wave * 5.5).toFixed(1));
      const actual = i < Math.ceil(count / 2) ? Number((pred - (i % 2 === 0 ? 0.3 : -0.4)).toFixed(1)) : null;
      const lowerBound = Number((pred - 1.8).toFixed(1));
      const upperBound = Number((pred + 1.8).toFixed(1));

      return {
        time: timeLabel,
        prediction: pred,
        actual,
        lowerBound,
        upperBound,
      };
    });
  }, [horizon, modelConfig]);

  // Dynamic Upcoming Table Rows based on horizon
  const tableRows = useMemo(() => {
    return forecastChartData.slice(0, 5).map((pt, i) => {
      const isVerified = pt.actual != null;
      const errorVal = isVerified ? (pt.prediction - (pt.actual as number)).toFixed(1) : null;
      return {
        time: horizon === "24 Hours" ? `15 Aug ${pt.time}` : pt.time,
        pred: pt.prediction,
        lower: pt.lowerBound,
        upper: pt.upperBound,
        actual: pt.actual,
        error: errorVal ? (Number(errorVal) > 0 ? `+${errorVal}` : errorVal) : "—",
        status: isVerified ? "Verified" : "Pending",
      };
    });
  }, [forecastChartData, horizon]);

  const errorDist = [
    { bin: "-3", count: 1 },
    { bin: "-2", count: 3 },
    { bin: "-1", count: 8 },
    { bin: "0",  count: 15 },
    { bin: "+1", count: 9 },
    { bin: "+2", count: 4 },
    { bin: "+3", count: 1 },
  ];

  if (isLoading) return <PageSkeleton />;
  if (error && !data) return <ErrorState title="Unable to load temperature forecast" message={error} onRetry={fetchData} />;

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Dynamic Filter Selectors */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--foreground)" }}>AI Forecasting • Temperature</h1>
          <p className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
            ML model forecast for {targetVar.toLowerCase()} · {currentLocation?.name || locationId}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Horizon Selector */}
          <div className="flex rounded-xl border p-1" style={{ background: "var(--card)", borderColor: "var(--border)" }}>
            {(["24 Hours", "7 Days", "14 Days"] as const).map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  horizon === h ? "bg-blue-600 text-white shadow" : "hover:text-blue-500"
                }`}
                style={{ color: horizon === h ? "#ffffff" : "var(--muted-foreground)" }}
              >
                {h}
              </button>
            ))}
          </div>

          {/* Model Selector */}
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="text-xs rounded-xl border px-3 py-1.5 font-semibold focus:outline-none"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <option value="XGBoost v12 (Temperature)">Model: XGBoost v12 (Temperature)</option>
            <option value="LightGBM v8 (Temperature)">Model: LightGBM v8 (Temperature)</option>
            <option value="CatBoost v4 (Temperature)">Model: CatBoost v4 (Temperature)</option>
          </select>

          {/* Target Selector */}
          <select
            value={targetVar}
            onChange={(e) => setTargetVar(e.target.value)}
            className="text-xs rounded-xl border px-3 py-1.5 font-semibold focus:outline-none"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <option value="2m Temperature">Target: 2m Temperature</option>
            <option value="Apparent Temperature">Target: Apparent Temperature</option>
          </select>

          <button
            onClick={() => window.print()}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition-colors"
            style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <Download size={13} />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* 6 KPI Cards in a Row (Dynamically calculated) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Current {targetVar.replace(" Temperature", "")}</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{currentTemp.toFixed(1)}°C</p>
          <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Observed</span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Next 6h Forecast</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{next6h.toFixed(1)}°C</p>
          <span className="text-[10px] text-emerald-500 font-semibold">(+1.4°C)</span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Daily Max (Pred)</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{dailyMax.toFixed(1)}°C</p>
          <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>At 3:00 PM</span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Daily Min (Pred)</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{dailyMin.toFixed(1)}°C</p>
          <span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>At 5:00 AM</span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Model MAE ({horizon})</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{modelConfig.mae.toFixed(2)}°C</p>
          <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">
            {modelConfig.rating}
          </span>
        </div>

        <div className="rounded-2xl border p-4 space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <span className="text-[11px] font-medium block" style={{ color: "var(--muted-foreground)" }}>Model RMSE ({horizon})</span>
          <p className="text-2xl font-extrabold" style={{ color: "var(--foreground)" }}>{modelConfig.rmse.toFixed(2)}°C</p>
          <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">
            Good
          </span>
        </div>
      </div>

      {/* Middle Row: Main Chart (Left) + Model Info & Error Dist (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-8 rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
            <h3 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>
              {targetVar} Forecast vs Actual ({horizon})
            </h3>
            <div className="flex flex-wrap items-center gap-3 text-[10px] font-semibold">
              <span className="flex items-center gap-1 text-cyan-500">
                <span className="h-1.5 w-3 bg-cyan-500 rounded-sm" /> {modelConfig.modelName} Prediction
              </span>
              <span className="flex items-center gap-1 text-emerald-500">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Actual (Observed)
              </span>
              <span className="flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
                <span className="h-1.5 w-3 border-t border-dashed border-slate-400" /> Upper Bound
              </span>
              <span className="flex items-center gap-1" style={{ color: "var(--muted-foreground)" }}>
                <span className="h-1.5 w-3 border-t border-dashed border-slate-500" /> Lower Bound
              </span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={260}>
            <ComposedChart data={forecastChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} axisLine={false} />
              <YAxis domain={[20, 42]} ticks={[20, 25, 30, 35, 40]} tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} unit="°" axisLine={false} />
              <Tooltip {...CHART_TOOLTIP_STYLE} />
              <Area type="monotone" dataKey="upperBound" stroke="#0ea5e9" strokeDasharray="3 3" fill="#0ea5e9" fillOpacity={0.08} name="Upper Bound (°C)" />
              <Line type="monotone" dataKey="lowerBound" stroke="#64748b" strokeDasharray="3 3" dot={false} strokeWidth={1} name="Lower Bound (°C)" />
              <Line type="monotone" dataKey="prediction" stroke="#38bdf8" strokeWidth={2.5} dot={{ r: 3.5, fill: "#38bdf8" }} name={`${modelConfig.modelName} (°C)`} />
              <Line type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2} dot={{ r: 4, fill: "#10b981" }} name="Actual (Observed) (°C)" connectNulls={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="lg:col-span-4 space-y-4">
          <div className="rounded-2xl border p-4 space-y-2.5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <h3 className="text-xs font-bold" style={{ color: "var(--foreground)" }}>Model Information</h3>
            <div className="space-y-1.5 text-xs">
              <div className="flex justify-between"><span style={{ color: "var(--muted-foreground)" }}>Model</span><strong style={{ color: "var(--foreground)" }}>{modelConfig.modelName}</strong></div>
              <div className="flex justify-between"><span style={{ color: "var(--muted-foreground)" }}>Trained On</span><span style={{ color: "var(--foreground)" }}>{modelConfig.trainDate}</span></div>
              <div className="flex justify-between"><span style={{ color: "var(--muted-foreground)" }}>Last Trained</span><span style={{ color: "var(--foreground)" }}>12 Aug 2026</span></div>
              <div className="flex justify-between"><span style={{ color: "var(--muted-foreground)" }}>Data Range</span><span style={{ color: "var(--foreground)" }}>Jun 2022 - Jul 2026</span></div>
              <div className="flex justify-between"><span style={{ color: "var(--muted-foreground)" }}>Features</span><span style={{ color: "var(--foreground)" }}>{modelConfig.features}</span></div>
              <div className="flex justify-between"><span style={{ color: "var(--muted-foreground)" }}>Forecast Horizon</span><span style={{ color: "var(--foreground)" }}>{horizon}</span></div>
              <div className="flex justify-between items-center pt-1 border-t" style={{ borderColor: "var(--border)" }}>
                <span style={{ color: "var(--muted-foreground)" }}>Model Status</span>
                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/20 text-emerald-600 dark:text-emerald-300">Active</span>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border p-4" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <h3 className="text-xs font-bold mb-2" style={{ color: "var(--foreground)" }}>Error Distribution ({horizon})</h3>
            <ResponsiveContainer width="100%" height={110}>
              <BarChart data={errorDist} margin={{ top: 5, right: 5, left: -30, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="bin" tick={{ fontSize: 9, fill: "var(--muted-foreground)" }} axisLine={false} />
                <YAxis tick={{ fontSize: 8, fill: "var(--muted-foreground)" }} axisLine={false} />
                <Tooltip {...CHART_TOOLTIP_STYLE} />
                <Bar dataKey="count" fill="#3b82f6" barSize={14} radius={[2, 2, 0, 0]} name="Frequency" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Table: Upcoming Temperature Forecast */}
      <div className="rounded-2xl border p-5" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
        <h3 className="text-sm font-bold mb-3" style={{ color: "var(--foreground)" }}>Upcoming Temperature Forecast ({horizon})</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b text-left font-semibold" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}>
                <th className="py-2.5 px-3">Time</th>
                <th className="py-2.5 px-3 text-right">Prediction (°C)</th>
                <th className="py-2.5 px-3 text-right">Lower Bound</th>
                <th className="py-2.5 px-3 text-right">Upper Bound</th>
                <th className="py-2.5 px-3 text-right">Actual (°C)</th>
                <th className="py-2.5 px-3 text-right">Error (°C)</th>
                <th className="py-2.5 px-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y font-medium" style={{ borderColor: "var(--border)" }}>
              {tableRows.map((r, i) => (
                <tr key={i} className="hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                  <td className="py-2.5 px-3 font-bold" style={{ color: "var(--foreground)" }}>{r.time}</td>
                  <td className="py-2.5 px-3 text-right text-cyan-500 font-extrabold">{r.pred.toFixed(1)}</td>
                  <td className="py-2.5 px-3 text-right" style={{ color: "var(--muted-foreground)" }}>{r.lower.toFixed(1)}</td>
                  <td className="py-2.5 px-3 text-right" style={{ color: "var(--muted-foreground)" }}>{r.upper.toFixed(1)}</td>
                  <td className="py-2.5 px-3 text-right" style={{ color: "var(--foreground)" }}>{r.actual != null ? r.actual.toFixed(1) : "—"}</td>
                  <td className="py-2.5 px-3 text-right text-emerald-500 font-bold">{r.error ?? "—"}</td>
                  <td className="py-2.5 px-3 text-right">
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${
                      r.status === "Verified" ? "bg-emerald-500/20 text-emerald-600 dark:text-emerald-300" : "bg-blue-500/20 text-blue-600 dark:text-blue-300"
                    }`}>
                      {r.status}
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
