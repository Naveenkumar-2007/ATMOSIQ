import { apiClient } from "@/lib/api";
import { CurrentWeather, DailyForecastItem, HourlyForecastItem, LocationInfo } from "@/types/weather";

export const weatherService = {
  async getLocations(): Promise<LocationInfo[]> {
    try {
      const data = await apiClient<LocationInfo[]>("/api/v1/locations");
      if (Array.isArray(data) && data.length > 0) return data;
    } catch (err) {
      console.warn("Failed to fetch locations from backend:", err);
    }
    return [
      { id: "kavali", name: "Kavali", latitude: 15.4833, longitude: 79.9167, timezone: "Asia/Kolkata", state: "Andhra Pradesh", country: "India" },
      { id: "hyderabad", name: "Hyderabad", latitude: 17.3850, longitude: 78.4867, timezone: "Asia/Kolkata", state: "Telangana", country: "India" },
    ];
  },

  async getCurrentWeather(locationId = "kavali"): Promise<CurrentWeather | null> {
    try {
      const combined = await apiClient<any>(`/api/v1/weather/combined/${encodeURIComponent(locationId)}`);
      const c = combined?.current;
      if (!c) return null;

      const weatherCode = c.weather_code ?? 0;
      let condition = "Clear Sky";
      if (weatherCode >= 1 && weatherCode <= 2) condition = "Partly Cloudy";
      else if (weatherCode === 3) condition = "Overcast Cloudy";
      else if (weatherCode >= 45 && weatherCode <= 48) condition = "Foggy";
      else if (weatherCode >= 51 && weatherCode <= 67) condition = "Rainy";
      else if (weatherCode >= 80) condition = "Showers / Storm";

      return {
        location: locationId,
        time: c.observation_time || new Date().toISOString(),
        temperature: c.temperature_2m ?? 0,
        feelsLike: c.apparent_temperature ?? c.temperature_2m ?? 0,
        condition,
        weatherCode,
        humidity: c.relative_humidity_2m ?? 0,
        dewPoint: c.dew_point_2m ?? (c.temperature_2m - (100 - (c.relative_humidity_2m || 0)) / 5),
        pressure: c.pressure_msl ?? 1013,
        windSpeed: c.wind_speed_10m ?? 0,
        windGusts: c.wind_gusts_10m ?? c.wind_speed_10m ?? 0,
        windDirection: c.wind_direction_10m ?? 0,
        windDirectionCompass: "N",
        cloudCover: c.cloud_cover ?? 0,
        visibility: c.visibility ? c.visibility / 1000 : 10,
        precipitation: 0.0,
        uvIndex: c.uv_index ?? 0,
        sunrise: c.sunrise || "06:00 AM",
        sunset: c.sunset || "06:30 PM",
      };
    } catch (err) {
      console.error(`Error loading current weather for ${locationId}:`, err);
      return null;
    }
  },

  async getHourlyForecast(locationId = "kavali"): Promise<HourlyForecastItem[]> {
    try {
      const combined = await apiClient<any>(`/api/v1/weather/combined/${encodeURIComponent(locationId)}`);
      const h = combined?.hourly;
      if (!h || !h.times || h.times.length === 0) return [];

      return h.times.slice(0, 24).map((t: string, i: number) => {
        const d = new Date(t);
        const hourStr = d.toLocaleTimeString([], { hour: "numeric", hour12: true });
        const code = h.weather_code?.[i] ?? 0;
        return {
          time: t,
          hour: hourStr,
          temperature: h.temperature_2m?.[i] ?? 0,
          feelsLike: h.apparent_temperature?.[i] ?? h.temperature_2m?.[i] ?? 0,
          precipitationProbability: h.precipitation_probability?.[i] ?? 0,
          precipitation: h.precipitation?.[i] ?? 0,
          windSpeed: h.wind_speed_10m?.[i] ?? 0,
          windDirection: "NW",
          weatherCode: code,
          condition: code === 0 ? "Clear" : code <= 2 ? "Partly Cloudy" : "Rain",
          humidity: h.relative_humidity_2m?.[i] ?? 0,
          pressure: 1012,
          cloudCover: h.cloud_cover?.[i] ?? 0,
        };
      });
    } catch (err) {
      console.error(`Error loading hourly forecast for ${locationId}:`, err);
      return [];
    }
  },

  async getDailyForecast(locationId = "kavali"): Promise<DailyForecastItem[]> {
    try {
      const combined = await apiClient<any>(`/api/v1/weather/combined/${encodeURIComponent(locationId)}`);
      const d = combined?.daily;
      if (!d || !d.dates || d.dates.length === 0) return [];

      return d.dates.map((dateStr: string, i: number) => {
        const dt = new Date(dateStr + "T00:00:00");
        const dayName = i === 0 ? "Today" : i === 1 ? "Tomorrow" : dt.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" });
        const code = d.weather_code?.[i] ?? 0;

        return {
          date: dateStr,
          dayName,
          weatherCode: code,
          condition: code === 0 ? "Clear Sky" : code <= 2 ? "Partly Cloudy" : "Rain Showers",
          tempMax: d.temperature_max?.[i] ?? 0,
          tempMin: d.temperature_min?.[i] ?? 0,
          precipitationSum: d.precipitation_sum?.[i] ?? 0,
          precipitationProbabilityMax: d.precipitation_probability_max?.[i] ?? 0,
          windSpeedMax: d.wind_speed_max?.[i] ?? 0,
          windGustsMax: d.wind_gusts_max?.[i] ?? 0,
          humidity: 70,
        };
      });
    } catch (err) {
      console.error(`Error loading daily forecast for ${locationId}:`, err);
      return [];
    }
  },
};

