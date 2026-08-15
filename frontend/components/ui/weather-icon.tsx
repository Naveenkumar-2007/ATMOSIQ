import React from "react";
import {
  Sun,
  Cloud,
  CloudSun,
  CloudRain,
  CloudLightning,
  CloudFog,
  CloudSnow,
  Wind,
  Droplets,
  Thermometer,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface WeatherIconProps {
  code?: number;
  condition?: string;
  className?: string;
  size?: number;
}

export function WeatherIcon({ code = 0, condition, className, size = 24 }: WeatherIconProps) {
  // If condition string provided
  if (condition) {
    const c = condition.toLowerCase();
    if (c.includes("thunder") || c.includes("storm")) return <CloudLightning size={size} className={cn("text-amber-400", className)} />;
    if (c.includes("heavy rain")) return <CloudRain size={size} className={cn("text-blue-400", className)} />;
    if (c.includes("rain") || c.includes("drizzle")) return <CloudRain size={size} className={cn("text-sky-400", className)} />;
    if (c.includes("snow")) return <CloudSnow size={size} className={cn("text-indigo-200", className)} />;
    if (c.includes("fog") || c.includes("mist")) return <CloudFog size={size} className={cn("text-slate-400", className)} />;
    if (c.includes("partly")) return <CloudSun size={size} className={cn("text-amber-300", className)} />;
    if (c.includes("cloud") || c.includes("overcast")) return <Cloud size={size} className={cn("text-slate-300", className)} />;
    if (c.includes("clear") || c.includes("sun")) return <Sun size={size} className={cn("text-amber-400", className)} />;
  }

  // Numerical WMO codes
  if (code === 0) {
    return <Sun size={size} className={cn("text-amber-400 animate-spin-slow", className)} />;
  }
  if (code <= 2) {
    return <CloudSun size={size} className={cn("text-amber-300", className)} />;
  }
  if (code === 3) {
    return <Cloud size={size} className={cn("text-slate-300", className)} />;
  }
  if (code === 45 || code === 48) {
    return <CloudFog size={size} className={cn("text-slate-400", className)} />;
  }
  if ((code >= 51 && code <= 57) || (code >= 61 && code <= 65)) {
    return <CloudRain size={size} className={cn("text-sky-400", className)} />;
  }
  if ((code >= 66 && code <= 67) || (code >= 80 && code <= 82)) {
    return <CloudRain size={size} className={cn("text-blue-500", className)} />;
  }
  if ((code >= 71 && code <= 77) || code === 85 || code === 86) {
    return <CloudSnow size={size} className={cn("text-indigo-200", className)} />;
  }
  if (code >= 95) {
    return <CloudLightning size={size} className={cn("text-amber-400", className)} />;
  }

  return <CloudSun size={size} className={cn("text-slate-300", className)} />;
}
