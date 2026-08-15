import React from "react";
import { MetricCard } from "@/components/ui/metric-card";
import { CurrentWeather } from "@/types/weather";
import { Thermometer, CloudRain, Droplets, Wind, Gauge, Eye } from "lucide-react";

interface MetricGridProps {
  weather: CurrentWeather;
  rainProbability?: number;
}

export function MetricGrid({ weather, rainProbability = 62 }: MetricGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
      <MetricCard
        title="Temperature"
        value={weather.temperature.toFixed(1)}
        unit="°C"
        subtitle={`Feels ${weather.feelsLike.toFixed(1)}°C`}
        trend={{ value: "+1.2°", direction: "up", label: "vs yesterday" }}
        icon={<Thermometer size={18} />}
        accentColor="orange"
      />

      <MetricCard
        title="Rain Probability"
        value={rainProbability}
        unit="%"
        subtitle="Moderate chance"
        trend={{ value: "+15%", direction: "up", label: "peak at 18:00" }}
        icon={<CloudRain size={18} />}
        accentColor="sky"
      />

      <MetricCard
        title="Humidity"
        value={weather.humidity}
        unit="%"
        subtitle={`Dew point ${weather.dewPoint.toFixed(1)}°C`}
        trend={{ value: "-4%", direction: "down", label: "afternoon dip" }}
        icon={<Droplets size={18} />}
        accentColor="cyan"
      />

      <MetricCard
        title="Wind Speed"
        value={weather.windSpeed.toFixed(1)}
        unit="km/h"
        subtitle={`Gusts ${weather.windGusts.toFixed(1)} km/h`}
        trend={{ value: "NW (318°)", direction: "neutral", label: "direction" }}
        icon={<Wind size={18} />}
        accentColor="blue"
      />

      <MetricCard
        title="Pressure"
        value={weather.pressure}
        unit="hPa"
        subtitle="MSL Barometer"
        trend={{ value: "-1.5 hPa", direction: "down", label: "steady tendency" }}
        icon={<Gauge size={18} />}
        accentColor="purple"
      />

      <MetricCard
        title="Visibility"
        value={weather.visibility.toFixed(1)}
        unit="km"
        subtitle="Optimal clearance"
        trend={{ value: "Good", direction: "neutral", label: "no fog" }}
        icon={<Eye size={18} />}
        accentColor="emerald"
      />
    </div>
  );
}
