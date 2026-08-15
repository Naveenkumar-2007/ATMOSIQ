export type LocationId = "kavali" | "hyderabad" | string;

export interface LocationInfo {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  state?: string;
  country?: string;
}

export interface CurrentWeather {
  location: string;
  time: string;
  temperature: number;
  feelsLike: number;
  condition: string;
  weatherCode: number;
  humidity: number;
  dewPoint: number;
  pressure: number;
  windSpeed: number;
  windGusts: number;
  windDirection: number;
  windDirectionCompass: string;
  cloudCover: number;
  visibility: number;
  precipitation: number;
  uvIndex?: number;
  airQuality?: {
    aqi: number;
    label: string;
    pm25: number;
    pm10: number;
    no2: number;
    so2: number;
  };
  sunrise?: string;
  sunset?: string;
}

export interface HourlyForecastItem {
  time: string;
  hour: string;
  temperature: number;
  feelsLike: number;
  precipitationProbability: number;
  precipitation: number;
  windSpeed: number;
  windDirection: string;
  weatherCode: number;
  condition: string;
  humidity: number;
  pressure: number;
  cloudCover: number;
}

export interface DailyForecastItem {
  date: string;
  dayName: string;
  weatherCode: number;
  condition: string;
  tempMax: number;
  tempMin: number;
  precipitationSum: number;
  precipitationProbabilityMax: number;
  windSpeedMax: number;
  windGustsMax: number;
  humidity: number;
}

export interface MLPrediction {
  task: string;
  horizonHours: number;
  model: string;
  modelVersion: string;
  prediction: number;
  p10?: number;
  p50?: number;
  p90?: number;
  lower?: number;
  upper?: number;
  rainProbability?: number;
  rainExpected?: boolean;
  condition?: string;
  direction?: string;
}

export interface FullPredictionResponse {
  location: string;
  horizon_hours: number;
  tasks: Record<string, MLPrediction | null>;
  rain_intensity?: "no_rain" | "light" | "moderate" | "heavy" | "very_heavy";
  risk?: {
    heat: { level: "minimal" | "elevated" | "high" | "extreme"; feels_like_c: number | null };
    heavy_rain: { level: "minimal" | "low" | "medium" | "high" | "extreme"; rain_24h_mm: number | null };
    high_wind: { level: "minimal" | "low" | "medium" | "high" | "extreme"; gust_kmh: number | null };
  };
}

export interface ModelLeaderboardItem {
  model: string;
  type: string;
  task: string;
  horizon: number;
  mae?: number;
  rmse?: number;
  mase?: number;
  skill?: number;
  status: "Champion" | "Candidate" | "Retired";
  versionId: string;
  trainingRunId?: string;
}

export interface DriftMetric {
  feature: string;
  dataType: string;
  psi: number;
  ksStat: number;
  pValue: number;
  threshold: number;
  status: "No Drift" | "Warning" | "Drift";
  detectedAt: string;
}

export interface AlertItem {
  id: string;
  alertType: string;
  severity: "info" | "warning" | "critical";
  scope: string;
  message: string;
  recommendation: string;
  status: "active" | "resolved" | "dismissed";
  createdAt: string;
  location?: string;
}

export interface SystemHealthStatus {
  api: "healthy" | "warning" | "down";
  database: "healthy" | "warning" | "down";
  mlService: "healthy" | "warning" | "down";
  dataIngestion: "healthy" | "warning" | "down";
  scheduler: "healthy" | "warning" | "down";
  latencyMs: number;
  cpuPercent: number;
  memoryPercent: number;
  errorRate: number;
  dataFreshness: string;
  totalPredictions24h: number;
}
