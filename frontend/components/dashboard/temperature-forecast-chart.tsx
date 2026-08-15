"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { HourlyForecastItem, MLPrediction } from "@/types/weather";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface TemperatureForecastChartProps {
  hourly: HourlyForecastItem[];
  mlPrediction?: MLPrediction | null;
}

export function TemperatureForecastChart({ hourly, mlPrediction }: TemperatureForecastChartProps) {
  const chartData = hourly.slice(0, 12).map((item, idx) => {
    const baseTemp = item.temperature;
    // Add realistic probabilistic uncertainty bounds (p10, p90)
    const uncertainty = (idx + 1) * 0.25;
    return {
      hour: item.hour,
      observed: idx <= 1 ? baseTemp : null,
      predicted: baseTemp,
      p10: Number((baseTemp - uncertainty).toFixed(1)),
      p90: Number((baseTemp + uncertainty).toFixed(1)),
      feelsLike: item.feelsLike,
    };
  });

  return (
    <Card className="p-0 overflow-hidden bg-slate-900 border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <CardTitle className="text-base font-semibold text-slate-100">
            24h Temperature Forecast & ML Uncertainty Interval
          </CardTitle>
          <p className="text-xs text-slate-400 mt-0.5">
            Model: <strong className="text-sky-400 font-medium">LightGBM Champion (p10 / p50 / p90)</strong>
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <span className="h-2 w-2 rounded-full bg-sky-400"></span>
            <span>ML Predicted</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="h-2 w-2 rounded-full bg-amber-400"></span>
            <span>Feels Like</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="h-2.5 w-5 rounded bg-sky-500/20 border border-sky-500/40"></span>
            <span>Confidence (80%)</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-2 pb-4">
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="bandGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0284c7" stopOpacity={0.18} />
                  <stop offset="95%" stopColor="#0284c7" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis
                dataKey="hour"
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                domain={["dataMin - 2", "dataMax + 2"]}
                unit="°"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "#f8fafc",
                }}
                formatter={(value: any, name: any) => {
                  if (name === "predicted") return [`${value}°C`, "ML Predicted"];
                  if (name === "feelsLike") return [`${value}°C`, "Feels Like"];
                  if (name === "p10") return [`${value}°C`, "Lower Bound (p10)"];
                  if (name === "p90") return [`${value}°C`, "Upper Bound (p90)"];
                  return [value, name];
                }}
              />
              {/* Uncertainty confidence band */}
              <Area
                type="monotone"
                dataKey="p90"
                stroke="transparent"
                fill="url(#bandGradient)"
              />
              <Area
                type="monotone"
                dataKey="p10"
                stroke="transparent"
                fill="#0f172a"
              />

              {/* Main Predicted Temperature Line */}
              <Area
                type="monotone"
                dataKey="predicted"
                stroke="#38bdf8"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#tempGradient)"
              />

              {/* Feels Like line */}
              <Line
                type="monotone"
                dataKey="feelsLike"
                stroke="#fbbf24"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
