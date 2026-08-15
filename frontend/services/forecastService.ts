import { apiClient } from "@/lib/api";
import { FullPredictionResponse, MLPrediction } from "@/types/weather";

export const forecastService = {
  async getFullPrediction(locationId = "kavali", horizonHours = 24): Promise<FullPredictionResponse | null> {
    try {
      const data = await apiClient<FullPredictionResponse>(
        `/api/v1/predict/full?location=${encodeURIComponent(locationId)}&horizon_hours=${horizonHours}`,
        { method: "POST" }
      );
      if (data && data.tasks) {
        return data;
      }
      return null;
    } catch (err) {
      console.error(`Error loading ML predictions for ${locationId}:`, err);
      return null;
    }
  },

  async getTaskPrediction(task: string, horizonHours = 24, locationId = "kavali"): Promise<MLPrediction | null> {
    try {
      return await apiClient<MLPrediction>(
        `/api/v1/predict/${encodeURIComponent(task)}?location=${encodeURIComponent(locationId)}&horizon_hours=${horizonHours}`,
        { method: "POST" }
      );
    } catch (err) {
      console.error(`Error loading prediction for task ${task}:`, err);
      return null;
    }
  },
};

