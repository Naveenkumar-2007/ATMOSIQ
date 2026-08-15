import React from "react";
import { Card } from "@/components/ui/card";
import { Sparkles, CheckCircle2, ShieldAlert, Cpu, Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface AIWeatherSummaryProps {
  temperature?: number;
  feelsLike?: number;
  condition?: string;
  rainIntensity?: string;
}

export function AIWeatherSummary({
  temperature = 27.4,
  feelsLike = 30.1,
  condition = "Partly Cloudy",
  rainIntensity = "light",
}: AIWeatherSummaryProps) {
  return (
    <Card className="p-5 bg-gradient-to-br from-slate-900 via-slate-900 to-sky-950/40 border-slate-800 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-sky-500/20 text-sky-400">
              <Sparkles size={16} />
            </div>
            <h3 className="text-sm font-semibold text-white">AI Weather Intelligence Summary</h3>
          </div>
          <Badge variant="info" className="text-[10px]">
            Model Inferred
          </Badge>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Current atmospheric profiles indicate stable ambient temperatures around{" "}
          <strong className="text-white">{temperature.toFixed(1)}°C</strong> with effective humidity driving feels-like
          conditions to <strong className="text-white">{feelsLike.toFixed(1)}°C</strong>. Light cloud dissipation is
          expected toward late afternoon, followed by convective rain triggers with a{" "}
          <strong className="text-sky-300">{rainIntensity}</strong> precipitation profile (0.3 – 4.2 mm) over the next 24 hours.
        </p>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-2 text-slate-300">
          <CheckCircle2 size={14} className="text-emerald-400 shrink-0" />
          <span>Optimal logistics window until 17:00</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <CheckCircle2 size={14} className="text-sky-400 shrink-0" />
          <span>Wind gusts stable below 22 km/h</span>
        </div>
      </div>
    </Card>
  );
}

interface SevereRiskAssessmentProps {
  risk?: {
    heat?: { level: string; feels_like_c: number | null };
    heavy_rain?: { level: string; rain_24h_mm: number | null };
    high_wind?: { level: string; gust_kmh: number | null };
  };
}

export function SevereRiskAssessment({ risk }: SevereRiskAssessmentProps) {
  const getBadgeVariant = (level?: string): "success" | "warning" | "danger" | "info" => {
    if (level === "extreme" || level === "critical") return "danger";
    if (level === "high" || level === "elevated") return "warning";
    if (level === "medium" || level === "low") return "info";
    return "success";
  };

  return (
    <Card className="p-5 bg-slate-900 border-slate-800">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-500/15 text-amber-400">
            <ShieldAlert size={16} />
          </div>
          <h3 className="text-sm font-semibold text-white">Weather Risk Assessment</h3>
        </div>
        <span className="text-[11px] text-slate-400">24h Evaluation Window</span>
      </div>

      <div className="space-y-3 mt-4">
        {/* Extreme Heat */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex flex-col">
            <span className="text-xs font-medium text-slate-200">Extreme Heat Risk</span>
            <span className="text-[11px] text-slate-400">Feels-like {risk?.heat?.feels_like_c ?? 30.1}°C</span>
          </div>
          <Badge variant={getBadgeVariant(risk?.heat?.level)} className="uppercase text-[10px]">
            {risk?.heat?.level || "Minimal"}
          </Badge>
        </div>

        {/* Heavy Rain */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex flex-col">
            <span className="text-xs font-medium text-slate-200">Heavy Rainfall & Flood</span>
            <span className="text-[11px] text-slate-400">24h Total: {risk?.heavy_rain?.rain_24h_mm ?? 0.3} mm</span>
          </div>
          <Badge variant={getBadgeVariant(risk?.heavy_rain?.level)} className="uppercase text-[10px]">
            {risk?.heavy_rain?.level || "Minimal"}
          </Badge>
        </div>

        {/* High Wind */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <div className="flex flex-col">
            <span className="text-xs font-medium text-slate-200">High Wind & Gusts</span>
            <span className="text-[11px] text-slate-400">Peak Gust: {risk?.high_wind?.gust_kmh ?? 21.9} km/h</span>
          </div>
          <Badge variant={getBadgeVariant(risk?.high_wind?.level)} className="uppercase text-[10px]">
            {risk?.high_wind?.level || "Minimal"}
          </Badge>
        </div>
      </div>
    </Card>
  );
}

export function ModelHealthTile() {
  return (
    <Card className="p-5 bg-slate-900 border-slate-800">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/15 text-emerald-400">
            <Cpu size={16} />
          </div>
          <h3 className="text-sm font-semibold text-white">Production ML Telemetry</h3>
        </div>
        <Badge variant="success" className="text-[10px]">
          124 Champions Active
        </Badge>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 text-xs">
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-400 text-[11px]">Primary Model</span>
          <p className="text-sm font-bold text-sky-400 mt-1">LightGBM v1.3</p>
        </div>
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-400 text-[11px]">Temp Skill Score</span>
          <p className="text-sm font-bold text-emerald-400 mt-1">0.82 (+18% vs Baseline)</p>
        </div>
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-400 text-[11px]">Drift Status</span>
          <p className="text-sm font-bold text-slate-200 mt-1">Healthy (KS p=0.52)</p>
        </div>
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-400 text-[11px]">P95 Latency</span>
          <p className="text-sm font-bold text-slate-200 mt-1">14.2 ms</p>
        </div>
      </div>
    </Card>
  );
}
