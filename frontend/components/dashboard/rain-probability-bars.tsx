"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface RainProbabilityBarsProps {
  rainfallMm?: number;
}

export function RainProbabilityBars({ rainfallMm = 0.32 }: RainProbabilityBarsProps) {
  const data = [
    { horizon: "Now", prob: 5, amount: 0.0 },
    { horizon: "+1h", prob: 12, amount: 0.0 },
    { horizon: "+3h", prob: 28, amount: 0.1 },
    { horizon: "+6h", prob: 62, amount: 1.8 },
    { horizon: "+12h", prob: 75, amount: 4.2 },
    { horizon: "+24h", prob: 45, amount: rainfallMm },
  ];

  return (
    <Card className="p-0 overflow-hidden bg-slate-900 border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <CardTitle className="text-base font-semibold text-slate-100">
            Precipitation & Rain Probability (Multi-Horizon)
          </CardTitle>
          <p className="text-xs text-slate-400 mt-0.5">
            Binary Classification Model: <strong className="text-cyan-400 font-medium">LightGBM (PR-AUC 0.76)</strong>
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <span className="h-2.5 w-2.5 rounded bg-sky-500"></span>
            <span>Rain Probability (%)</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
            <span>Amount (mm)</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-2 pb-4">
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="horizon" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} unit="%" domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "#f8fafc",
                }}
                formatter={(value: any, name: any) => {
                  if (name === "prob") return [`${value}%`, "Rain Probability"];
                  if (name === "amount") return [`${value} mm`, "Expected Rain"];
                  return [value, name];
                }}
              />
              <Bar dataKey="prob" radius={[6, 6, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.prob > 50 ? "#0284c7" : entry.prob > 25 ? "#38bdf8" : "#64748b"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
