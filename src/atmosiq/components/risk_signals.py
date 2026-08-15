class RiskSignals:
    def __init__(self, risk_config):
        self.cfg = risk_config or {}

    def _band(self, value, bands):
        if value is None:
            return "minimal"
        try:
            val = float(value)
        except (ValueError, TypeError):
            return "minimal"

        if "extreme" in bands and val >= bands["extreme"]:
            return "extreme"
        if "high" in bands and val >= bands["high"]:
            return "high"
        if "elevated" in bands and val >= bands["elevated"]:
            return "elevated"
        if "medium" in bands and val >= bands["medium"]:
            return "medium"
        if "low" in bands and val >= bands["low"]:
            return "low"
        return "minimal"

    def heat_risk(self, feels_like):
        bands = self.cfg.get("heat_feels_like_c", {})
        return {"level": self._band(feels_like, bands), "feels_like_c": feels_like}

    def heavy_rain_risk(self, rain_24h_mm):
        bands = self.cfg.get("heavy_rain_24h_mm", {})
        return {"level": self._band(rain_24h_mm, bands), "rain_24h_mm": rain_24h_mm}

    def high_wind_risk(self, gust_kmh):
        bands = self.cfg.get("wind_gust_kmh", {})
        return {"level": self._band(gust_kmh, bands), "gust_kmh": gust_kmh}

    def compute(self, feels_like=None, rain_24h_mm=None, gust_kmh=None):
        return {
            "heat": self.heat_risk(feels_like),
            "heavy_rain": self.heavy_rain_risk(rain_24h_mm),
            "high_wind": self.high_wind_risk(gust_kmh),
        }
