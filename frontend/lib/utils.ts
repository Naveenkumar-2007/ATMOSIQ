import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTemp(celsius: number | null | undefined, unit: "C" | "F" = "C"): string {
  if (celsius === null || celsius === undefined || isNaN(celsius)) return "--";
  if (unit === "F") {
    return `${Math.round((celsius * 9) / 5 + 32)}°F`;
  }
  return `${Math.round(celsius * 10) / 10}°C`;
}

export function formatSpeed(kmh: number | null | undefined, unit: "km/h" | "mph" | "m/s" = "km/h"): string {
  if (kmh === null || kmh === undefined || isNaN(kmh)) return "--";
  if (unit === "mph") return `${(kmh * 0.621371).toFixed(1)} mph`;
  if (unit === "m/s") return `${(kmh / 3.6).toFixed(1)} m/s`;
  return `${kmh.toFixed(1)} km/h`;
}

export function formatPressure(hpa: number | null | undefined): string {
  if (hpa === null || hpa === undefined || isNaN(hpa)) return "--";
  return `${Math.round(hpa)} hPa`;
}

export function formatRain(mm: number | null | undefined): string {
  if (mm === null || mm === undefined || isNaN(mm)) return "0.0 mm";
  return `${mm.toFixed(1)} mm`;
}
