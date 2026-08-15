import { apiClient } from "@/lib/api";
import { AlertItem, DriftMetric, SystemHealthStatus, HealthStatus } from "@/types/weather";

export const monitoringService = {
  async getDriftReport(): Promise<DriftMetric[]> {
    try {
      const data = await apiClient<any>("/api/v1/monitoring/drift");
      if (data && Array.isArray(data) && data.length > 0) {
        return data.map((d: any) => ({
          feature: d.feature || "unknown",
          dataType: "numeric",
          psi: d.psi ?? 0,
          ksStat: d.ks_statistic ?? 0,
          pValue: d.p_value ?? 0,
          threshold: d.threshold ?? 0.25,
          status: d.detected ? "Drift" : (d.psi > 0.15 ? "Warning" : "No Drift"),
          detectedAt: d.timestamp || new Date().toISOString(),
        }));
      }
    } catch {
      // Return empty array when API is unavailable
    }

    return [];
  },

  async getSystemHealth(): Promise<SystemHealthStatus> {
    try {
      const ready = await apiClient<any>("/health/ready");
      const live = await apiClient<any>("/health/live");
      if (ready && live) {
        const healthData = await apiClient<any>("/api/v1/system/health").catch(() => null);
        const apiStatus: HealthStatus = ready.status === "ready" ? "healthy" : "warning";
        return {
          api: apiStatus,
          database: apiStatus,
          mlService: (healthData?.ml_service as HealthStatus) || "healthy",
          dataIngestion: (healthData?.data_ingestion as HealthStatus) || "healthy",
          scheduler: (healthData?.scheduler as HealthStatus) || "healthy",
          latencyMs: healthData?.api_latency_ms || 0,
          cpuPercent: healthData?.cpu_percent || 0,
          memoryPercent: healthData?.memory_percent || 0,
          errorRate: healthData?.error_rate || 0,
          dataFreshness: healthData?.last_ingestion_ago || "Unknown",
          totalPredictions24h: healthData?.predictions_24h || 0,
        };
      }
    } catch {
      // Return degraded state when API is unavailable
    }

    return {
      api: "down",
      database: "down",
      mlService: "warning",
      dataIngestion: "warning",
      scheduler: "warning",
      latencyMs: 0,
      cpuPercent: 0,
      memoryPercent: 0,
      errorRate: 0,
      dataFreshness: "Unable to connect",
      totalPredictions24h: 0,
    };
  },
};

export const alertService = {
  async getAlerts(): Promise<AlertItem[]> {
    try {
      const data = await apiClient<any[]>(`/api/v1/alerts`);
      if (Array.isArray(data) && data.length > 0) {
        return data.map((a, index) => ({
          id: a.id || `alert-${index}-${Date.now()}`,
          alertType: a.alert_type || a.message || "Alert",
          severity: a.severity || "info",
          scope: a.scope || "location",
          message: a.message || "",
          recommendation: a.recommendation || "",
          status: a.status || "active",
          createdAt: a.created_at || new Date().toISOString(),
          location: a.location || "Unknown",
        }));
      }
    } catch {
      // Return empty array when API is unavailable
    }

    return [];
  },
};
