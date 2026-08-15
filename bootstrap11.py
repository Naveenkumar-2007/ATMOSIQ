# bootstrap11.py -> run: python bootstrap11.py   (supersedes previous frontend/config)
import os

W = {}

# ---------- Production config: many Indian cities/towns, data up to YESTERDAY ----------
W["config/atmosiq.yaml"] = r'''
project: AtmosIQ
locations:
  - { id: kavali, name: Kavali, latitude: 15.4833, longitude: 79.9167, timezone: Asia/Kolkata }
  - { id: nellore, name: Nellore, latitude: 14.4426, longitude: 79.9865, timezone: Asia/Kolkata }
  - { id: tirupati, name: Tirupati, latitude: 13.6288, longitude: 79.4192, timezone: Asia/Kolkata }
  - { id: ongole, name: Ongole, latitude: 15.5057, longitude: 80.0499, timezone: Asia/Kolkata }
  - { id: chittoor, name: Chittoor, latitude: 13.2172, longitude: 79.1003, timezone: Asia/Kolkata }
  - { id: vijayawada, name: Vijayawada, latitude: 16.5062, longitude: 80.6480, timezone: Asia/Kolkata }
  - { id: guntur, name: Guntur, latitude: 16.3067, longitude: 80.4428, timezone: Asia/Kolkata }
  - { id: kurnool, name: Kurnool, latitude: 15.8281, longitude: 78.0373, timezone: Asia/Kolkata }
  - { id: visakhapatnam, name: Visakhapatnam, latitude: 17.6868, longitude: 83.2185, timezone: Asia/Kolkata }
  - { id: kakinada, name: Kakinada, latitude: 16.9891, longitude: 82.2475, timezone: Asia/Kolkata }
  - { id: rajahmundry, name: Rajahmundry, latitude: 17.0005, longitude: 81.8040, timezone: Asia/Kolkata }
  - { id: chennai, name: Chennai, latitude: 13.0827, longitude: 80.2707, timezone: Asia/Kolkata }
  - { id: tiruchirappalli, name: Tiruchirappalli, latitude: 10.7905, longitude: 79.1372, timezone: Asia/Kolkata }
  - { id: salem, name: Salem, latitude: 11.6643, longitude: 78.1460, timezone: Asia/Kolkata }
  - { id: coimbatore, name: Coimbatore, latitude: 11.0168, longitude: 76.9558, timezone: Asia/Kolkata }
  - { id: madurai, name: Madurai, latitude: 9.9252, longitude: 78.1198, timezone: Asia/Kolkata }
  - { id: bengaluru, name: Bengaluru, latitude: 12.9716, longitude: 77.5946, timezone: Asia/Kolkata }
  - { id: mysuru, name: Mysuru, latitude: 12.2958, longitude: 76.6394, timezone: Asia/Kolkata }
  - { id: mangaluru, name: Mangaluru, latitude: 12.9141, longitude: 74.8560, timezone: Asia/Kolkata }
  - { id: hubli, name: Hubli, latitude: 15.3647, longitude: 75.1240, timezone: Asia/Kolkata }
  - { id: kochi, name: Kochi, latitude: 9.9312, longitude: 76.2673, timezone: Asia/Kolkata }
  - { id: thiruvananthapuram, name: Thiruvananthapuram, latitude: 8.5241, longitude: 76.9366, timezone: Asia/Kolkata }
  - { id: hyderabad, name: Hyderabad, latitude: 17.3850, longitude: 78.4867, timezone: Asia/Kolkata }
  - { id: warangal, name: Warangal, latitude: 17.9689, longitude: 79.5941, timezone: Asia/Kolkata }
  - { id: mumbai, name: Mumbai, latitude: 19.0760, longitude: 72.8777, timezone: Asia/Kolkata }
  - { id: pune, name: Pune, latitude: 18.5204, longitude: 73.8567, timezone: Asia/Kolkata }
  - { id: nagpur, name: Nagpur, latitude: 21.1458, longitude: 79.0882, timezone: Asia/Kolkata }
  - { id: nashik, name: Nashik, latitude: 19.9975, longitude: 73.7898, timezone: Asia/Kolkata }
  - { id: delhi, name: Delhi, latitude: 28.7041, longitude: 77.1025, timezone: Asia/Kolkata }
  - { id: jaipur, name: Jaipur, latitude: 26.9124, longitude: 75.7873, timezone: Asia/Kolkata }
  - { id: lucknow, name: Lucknow, latitude: 26.8467, longitude: 80.9462, timezone: Asia/Kolkata }
  - { id: kanpur, name: Kanpur, latitude: 26.4499, longitude: 80.3319, timezone: Asia/Kolkata }
  - { id: kolkata, name: Kolkata, latitude: 22.5726, longitude: 88.3639, timezone: Asia/Kolkata }
  - { id: bhubaneswar, name: Bhubaneswar, latitude: 20.2961, longitude: 85.8245, timezone: Asia/Kolkata }
  - { id: patna, name: Patna, latitude: 25.5941, longitude: 85.1376, timezone: Asia/Kolkata }
  - { id: ranchi, name: Ranchi, latitude: 23.3441, longitude: 85.3096, timezone: Asia/Kolkata }
  - { id: guwahati, name: Guwahati, latitude: 26.1445, longitude: 91.7362, timezone: Asia/Kolkata }
  - { id: ahmedabad, name: Ahmedabad, latitude: 23.0225, longitude: 72.5714, timezone: Asia/Kolkata }
  - { id: surat, name: Surat, latitude: 21.1702, longitude: 72.8311, timezone: Asia/Kolkata }
  - { id: indore, name: Indore, latitude: 22.7196, longitude: 75.8577, timezone: Asia/Kolkata }
  - { id: bhopal, name: Bhopal, latitude: 23.2599, longitude: 77.4126, timezone: Asia/Kolkata }
historical:
  start_date: "2024-01-01"
  end_date: "yesterday"
provider:
  name: open_meteo
  timeout_seconds: 60
  max_retries: 3
  backoff_base_seconds: 2.0
splits: { train: 0.70, validation: 0.15, test: 0.15 }
validation:
  ranges:
    relative_humidity_2m: [0, 100]
    precipitation: [0, 600]
    rain: [0, 600]
    showers: [0, 600]
    snowfall: [0, 300]
    precipitation_probability: [0, 100]
    wind_speed_10m: [0, 150]
    wind_gusts_10m: [0, 200]
    wind_direction_10m: [0, 360]
    pressure_msl: [870, 1085]
    surface_pressure: [400, 1100]
    cloud_cover: [0, 100]
    visibility: [0, 100000]
    temperature_2m: [-90, 60]
    dew_point_2m: [-100, 40]
    apparent_temperature: [-100, 70]
  max_missing_fraction: 0.25
  max_gap_hours: 12
rain:
  occurrence_threshold_mm: 0.2
  intensity_mm: { light: 2.5, moderate: 7.5, heavy: 64.5, very_heavy: 115.6 }
risk:
  heat_feels_like_c: { elevated: 35, high: 40, extreme: 45 }
  heavy_rain_24h_mm: { low: 2.5, medium: 15, high: 60, extreme: 120 }
  wind_gust_kmh: { low: 30, medium: 50, high: 75 }
quality_gate:
  must_beat_persistence: true
  min_skill_vs_persistence: 0.02
  max_mase: 1.5
  min_rain_pr_auc: 0.50
  min_condition_accuracy: 0.20
  max_latency_ms: 2000.0
  require_manual_approval: true
drift: { psi_threshold: 0.25, ks_alpha: 0.05, confirmation_events: 2 }
alerts: { cooldown_minutes: 30 }
deep: { sequence_length: 24, epochs: 3, batch_size: 64, patience: 2 }
tuning: { n_trials: 5, cv_splits: 2 }
'''

# ---------- resolve "yesterday"/"today" in dates ----------
W["src/atmosiq/common/timeutils.py"] = r'''
from datetime import datetime, timedelta, timezone


def now_utc():
    return datetime.now(timezone.utc)


def floor_hour(dt):
    return dt.replace(minute=0, second=0, microsecond=0)


def lead_time_hours(issue_time, valid_time):
    return (valid_time - issue_time) / timedelta(hours=1)


def resolve_date(value):
    v = str(value).strip().lower()
    if v == "yesterday":
        return (now_utc() - timedelta(days=1)).strftime("%Y-%m-%d")
    if v == "today":
        return now_utc().strftime("%Y-%m-%d")
    return str(value)
'''

W["src/atmosiq/components/data_ingestion.py"] = r'''
import os
import sys
import uuid

from atmosiq.common.timeutils import now_utc, resolve_date
from atmosiq.db.models import IngestionRun
from atmosiq.db.repositories import ForecastRepository, LocationRepository, ObservationRepository, RunRepository
from atmosiq.entity.artifact_entity import DataIngestionArtifact
from atmosiq.entity.config_entity import DataIngestionConfig
from atmosiq.exception.exception import AtmosIQException
from atmosiq.logging.logger import logging
from atmosiq.utils.main_utils.utils import save_parquet, write_json_file

logger = logging.getLogger("atmosiq.components.data_ingestion")


class DataIngestion:
    def __init__(self, data_ingestion_config, provider, session=None):
        try:
            self.config = data_ingestion_config
            self.provider = provider
            self.session = session
        except Exception as e:
            raise AtmosIQException(e, sys)

    def _ingest_location(self, location):
        start = resolve_date(self.config.app.raw["historical"]["start_date"])
        end = resolve_date(self.config.app.raw["historical"]["end_date"])
        historical = self.provider.fetch_historical(location, start, end)
        write_json_file(os.path.join(self.config.raw_dir, f"{location['id']}_historical_raw.json"), historical.raw)
        obs_count = 0
        fc_count = 0
        if self.session is not None:
            LocationRepository(self.session).upsert(self.config.app.locations)
            obs_count = ObservationRepository(self.session).upsert_observations(location["id"], self.provider.name, historical.hourly)
            forecast = self.provider.fetch_forecast(location)
            save_parquet(forecast.hourly, os.path.join(self.config.forecast_dir, f"{location['id']}_forecast.parquet"))
            write_json_file(os.path.join(self.config.forecast_dir, f"{location['id']}_forecast_raw.json"), forecast.raw)
            fc_count = ForecastRepository(self.session).store_forecast_run(location["id"], self.provider.name, forecast.issue_time, forecast.meta.request_id, forecast.hourly)
        bronze = historical.hourly.copy()
        bronze["latitude"] = float(location["latitude"])
        bronze["longitude"] = float(location["longitude"])
        save_parquet(bronze, os.path.join(self.config.bronze_dir, f"{location['id']}_hourly.parquet"))
        if not historical.daily.empty:
            save_parquet(historical.daily, os.path.join(self.config.bronze_dir, f"{location['id']}_daily.parquet"))
        return obs_count, fc_count

    def initiate_data_ingestion(self):
        try:
            run_id = f"ing_{uuid.uuid4().hex[:12]}"
            total_obs = 0
            total_fc = 0
            for location in self.config.app.locations:
                logger.info("ingesting location", extra={"ctx_location_id": location["id"]})
                obs, fc = self._ingest_location(location)
                total_obs += obs
                total_fc += fc
                if self.session is not None:
                    RunRepository(self.session).add_ingestion_run(IngestionRun(
                        id=f"{run_id}_{location['id']}", location_id=location["id"], provider=self.provider.name,
                        started_at=now_utc(), finished_at=now_utc(), status="success",
                        observation_count=obs, forecast_count=fc, meta={"run_id": run_id},
                    ))
            return DataIngestionArtifact(
                raw_dir=self.config.raw_dir, bronze_dir=self.config.bronze_dir, forecast_dir=self.config.forecast_dir,
                ingestion_run_id=run_id, observation_count=total_obs, forecast_count=total_fc,
            )
        except Exception as e:
            raise AtmosIQException(e, sys)
'''

W["src/atmosiq/ingest_india.py"] = r'''
from concurrent.futures import ThreadPoolExecutor, as_completed

from atmosiq.common.timeutils import resolve_date
from atmosiq.db.repositories import LocationRepository, ObservationRepository
from atmosiq.db.session import get_session
from atmosiq.entity.config_entity import AppConfig
from atmosiq.logging.logger import logging
from atmosiq.providers import get_provider

logger = logging.getLogger("atmosiq.ingest_india")

MAX_WORKERS = 3


def year_chunks(start_date_str, end_date_str):
    start_year = int(start_date_str[:4])
    end_year = int(end_date_str[:4])
    for y in range(start_year, end_year + 1):
        s = f"{y}-01-01" if y > start_year else start_date_str
        e = f"{y}-12-31" if y < end_year else end_date_str
        yield s, e


def ingest_location(provider, location, start_date, end_date):
    total = 0
    for start, end in year_chunks(start_date, end_date):
        session = get_session()
        try:
            bundle = provider.fetch_historical(location, start, end)
            LocationRepository(session).upsert([location])
            n = ObservationRepository(session).upsert_observations(location["id"], provider.name, bundle.hourly)
            total += n
            logger.info("chunk ok", extra={"ctx_location_id": location["id"], "ctx_range": f"{start}..{end}", "ctx_rows": n})
        except Exception as e:
            logger.error(f"chunk failed {location['id']} {start}..{end}: {e}")
        finally:
            session.close()
    return location["id"], total


def main():
    app = AppConfig()
    provider = get_provider(app.raw["provider"]["name"], app.raw["provider"])
    start_date = resolve_date(app.raw["historical"]["start_date"])
    end_date = resolve_date(app.raw["historical"]["end_date"])
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(ingest_location, provider, loc, start_date, end_date) for loc in app.locations]
        for fut in as_completed(futures):
            loc_id, n = fut.result()
            results[loc_id] = n
    print("Ingested rows per location:", results)
    print("Total:", sum(results.values()))


if __name__ == "__main__":
    main()
'''

# ---------- Startup-grade frontend (light content + dark sidebar, like the mockups) ----------
W["frontend/index.html"] = r'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AtmosIQ - AI Weather Intelligence</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header id="topbar">
    <div class="brand">Atmos<span>IQ</span></div>
    <select id="locSelect"></select>
    <span id="dateLabel" class="muted"></span>
    <div class="spacer"></div>
    <button id="refreshBtn" title="Refresh">&#8635;</button>
  </header>
  <div class="layout">
    <nav id="sidebar"></nav>
    <main id="content"></main>
  </div>
  <script src="app.js"></script>
</body>
</html>
'''

W["frontend/styles.css"] = r'''
:root{
  --bg:#f4f6fb; --panel:#ffffff; --border:#e3e8f0; --text:#0f172a; --muted:#64748b;
  --accent:#2563eb; --accent2:#3b82f6; --side:#0b1c33; --side-text:#b8c6dd;
  --success:#16a34a; --warning:#d97706; --danger:#dc2626; --violet:#7c3aed;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,"Segoe UI",system-ui,sans-serif;background:var(--bg);color:var(--text)}
#topbar{display:flex;align-items:center;gap:12px;padding:12px 20px;background:var(--panel);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:20}
.brand{font-size:20px;font-weight:800}.brand span{color:var(--accent2)}
#topbar select,#topbar button{background:#fff;color:var(--text);border:1px solid var(--border);border-radius:8px;padding:7px 10px;font-size:13px}
.spacer{flex:1}.muted{color:var(--muted);font-size:12px}
.layout{display:flex;min-height:calc(100vh - 53px)}
#sidebar{width:230px;background:var(--side);padding:16px 10px}
#sidebar .group{color:var(--side-text);opacity:.7;font-size:11px;text-transform:uppercase;letter-spacing:.06em;margin:16px 8px 6px}
#sidebar a{display:flex;align-items:center;gap:9px;color:var(--side-text);text-decoration:none;padding:9px 12px;border-radius:8px;font-size:13.5px;margin-bottom:2px}
#sidebar a:hover{background:rgba(255,255,255,.06);color:#fff}
#sidebar a.active{background:var(--accent);color:#fff}
#content{flex:1;padding:22px;overflow-y:auto}
.page-title{font-size:21px;margin-bottom:16px}
.grid{display:grid;gap:16px}
.cols-2{grid-template-columns:repeat(2,1fr)}.cols-3{grid-template-columns:repeat(3,1fr)}.cols-4{grid-template-columns:repeat(4,1fr)}
@media(max-width:1100px){.cols-3,.cols-4{grid-template-columns:repeat(2,1fr)}}
.card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px;box-shadow:0 1px 2px rgba(16,24,40,.05)}
.card h3{font-size:12px;color:var(--muted);margin-bottom:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.card .sub{color:var(--muted);font-size:12px;margin-top:6px}
.stat-label{color:var(--muted);font-size:11px;text-transform:uppercase}
.stat-value{font-size:24px;font-weight:700;margin-top:2px}
.stat-sub{color:var(--muted);font-size:12px;margin-top:2px}
.hero{background:linear-gradient(135deg,#2563eb,#1e40af);color:#fff;border-radius:14px;padding:24px;display:flex;gap:24px;align-items:center;flex-wrap:wrap}
.hero .icon{font-size:60px}
.hero .big{font-size:48px;font-weight:800}
.hero .cond{font-size:15px}
.hero .feels{opacity:.85;font-size:13px}
.mini{display:flex;gap:26px;flex-wrap:wrap}
.mini div b{display:block;font-size:16px}
.mini div span{opacity:.8;font-size:11px;text-transform:uppercase}
.kv{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px dashed var(--border);font-size:13px}
.kv:last-child{border-bottom:none}.kv .k{color:var(--muted)}
table{width:100%;border-collapse:collapse}
th,td{padding:8px 10px;border-bottom:1px solid var(--border);text-align:left;font-size:13px}
th{color:var(--muted);font-weight:500;font-size:12px}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:11.5px;font-weight:600}
.badge-success{background:rgba(22,163,74,.12);color:var(--success)}
.badge-warning{background:rgba(217,119,6,.12);color:var(--warning)}
.badge-danger{background:rgba(220,38,38,.12);color:var(--danger)}
.badge-info{background:rgba(37,99,235,.12);color:var(--accent)}
.badge-muted{background:rgba(100,116,139,.12);color:var(--muted)}
.badge-violet{background:rgba(124,58,237,.12);color:var(--violet)}
.pills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.pills button{background:#fff;color:var(--muted);border:1px solid var(--border);border-radius:999px;padding:5px 14px;font-size:12px;cursor:pointer}
.pills button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
svg{display:block;width:100%;height:auto}
.legend{display:flex;gap:14px;margin-top:8px;flex-wrap:wrap}
.legend span{font-size:12px;color:var(--muted);display:inline-flex;align-items:center;gap:6px}
.legend i{width:10px;height:10px;border-radius:2px;display:inline-block}
.risk-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px dashed var(--border)}
.risk-row:last-child{border-bottom:none}
.model-tag{font-size:11px;color:var(--violet);background:rgba(124,58,237,.08);border-radius:6px;padding:2px 8px}
.empty{color:var(--muted);font-size:13px;padding:12px;border:1px dashed var(--border);border-radius:10px;background:#fff}
.btn{background:var(--accent);color:#fff;border:none;border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer}
'''

W["frontend/app.js"] = r'''
const API_BASE = "";
const state = { location: "kavali", horizon: 24 };
const HORIZONS = [1, 3, 6, 12, 24, 48, 72];

const PAGES = [
  { group: "", route: "overview", title: "Overview", icon: "▦", render: renderOverview },
  { group: "Forecast", route: "current", title: "Current Weather", icon: "☀", render: renderCurrent },
  { group: "", route: "hourly", title: "Hourly Forecast", icon: "🕐", render: renderHourly },
  { group: "", route: "daily", title: "Daily Forecast", icon: "📅", render: renderDaily },
  { group: "", route: "rainfall", title: "Rainfall", icon: "🌧", render: renderRainfall },
  { group: "", route: "wind", title: "Wind", icon: "💨", render: renderWind },
  { group: "", route: "map", title: "Weather Map", icon: "🗺", render: renderMap },
  { group: "", route: "historical", title: "Historical", icon: "🗄", render: renderHistorical },
  { group: "ML Operations", route: "forecast", title: "ML Forecast", icon: "🤖", render: renderForecast },
  { group: "", route: "accuracy", title: "Forecast Accuracy", icon: "🎯", render: renderAccuracy },
  { group: "", route: "models", title: "Models", icon: "🏆", render: renderModels },
  { group: "", route: "modeldetails", title: "Model Details", icon: "🔍", render: renderModelDetails },
  { group: "", route: "drift", title: "Drift Monitoring", icon: "📈", render: renderDrift },
  { group: "", route: "alerts", title: "Alerts", icon: "🔔", render: renderAlerts },
  { group: "Data", route: "explorer", title: "Data Explorer", icon: "🧾", render: renderExplorer },
  { group: "", route: "reports", title: "Reports", icon: "📑", render: renderReports },
  { group: "System", route: "health", title: "System Health", icon: "🩺", render: renderHealth },
  { group: "", route: "settings", title: "Settings", icon: "⚙", render: renderSettings },
];

async function api(path, method = "GET") {
  const res = await fetch(API_BASE + path, { method });
  if (!res.ok) throw new Error(`API ${path} -> ${res.status}`);
  return res.json();
}
const post = (p) => api(p, "POST");
const safe = (fn, fb) => fn().catch(() => fb);

function el(tag, attrs = {}, children = []) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "className") n.className = v; else if (k === "innerHTML") n.innerHTML = v; else n.setAttribute(k, v);
  }
  for (const c of children) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  return n;
}
const card = (t, b, s) => { const c = el("div", { className: "card" }, [el("h3", {}, [t])]); c.appendChild(b); if (s) c.appendChild(el("div", { className: "sub" }, [s])); return c; };
const f1 = (v) => (v == null || isNaN(v) ? "-" : Number(v).toFixed(1));
const f0 = (v) => (v == null || isNaN(v) ? "-" : Math.round(Number(v)));
const pct = (v) => (v == null || isNaN(v) ? "-" : Math.round(Number(v) * 100) + "%");
const badge = (t, k = "info") => el("span", { className: `badge badge-${k}` }, [String(t)]);
const empty = (m) => el("div", { className: "empty" }, [m]);
function table(h, rows) {
  return el("table", {}, [
    el("thead", {}, [el("tr", {}, h.map((x) => el("th", {}, [x])))]),
    el("tbody", {}, rows.map((r) => el("tr", {}, r.map((c) => el("td", {}, [typeof c === "object" ? c : String(c)]))))),
  ]);
}
function conditionIcon(code) {
  if (code == null) return "☁️"; code = Number(code);
  if (code === 0) return "☀️"; if (code <= 2) return "🌤️"; if (code === 3) return "☁️";
  if (code === 45 || code === 48) return "🌫️"; if (code <= 67) return "🌧️";
  if (code <= 77 || code === 85 || code === 86) return "❄️"; if (code <= 82) return "🌧️";
  if (code >= 95) return "⛈️"; return "☁️";
}
function tempColor(t) { if (t <= 5) return "#0ea5e9"; if (t <= 15) return "#16a34a"; if (t <= 25) return "#eab308"; if (t <= 33) return "#f97316"; return "#dc2626"; }
function riskKind(l) { if (!l) return "muted"; if (["extreme", "high"].includes(l)) return "danger"; if (["elevated", "medium"].includes(l)) return "warning"; if (["low"].includes(l)) return "info"; return "success"; }

function svgEl(t, a) { const n = document.createElementNS("http://www.w3.org/2000/svg", t); for (const [k, v] of Object.entries(a)) n.setAttribute(k, v); return n; }
function scaleAll(vals, W, H, pad) {
  const nums = vals.filter((v) => v != null && !isNaN(v)); if (!nums.length) return null;
  const min = Math.min(...nums), max = Math.max(...nums);
  return { x: (i, n) => pad + (i * (W - 2 * pad)) / Math.max(n - 1, 1), y: (v) => H - pad - ((v - min) / Math.max(max - min, 1e-9)) * (H - 2 * pad), min, max };
}
function lineChart(labels, series, height = 200) {
  const W = 600, H = height, pad = 30; const s = scaleAll(series.flatMap((x) => x.values), W, H, pad);
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  if (!s) { svg.appendChild(svgEl("text", { x: 20, y: 30, fill: "#64748b", "font-size": 12 })).textContent = "No data"; return svg; }
  for (const ser of series) {
    const pts = ser.values.map((v, i) => (v == null || isNaN(v) ? null : `${s.x(i, ser.values.length)},${s.y(v)}`)).filter(Boolean).join(" ");
    svg.appendChild(svgEl("polyline", { points: pts, fill: "none", stroke: ser.color, "stroke-width": 2 }));
  }
  svg.appendChild(svgEl("text", { x: pad, y: 14, fill: "#64748b", "font-size": 10 })).textContent = f1(s.max);
  svg.appendChild(svgEl("text", { x: pad, y: H - 6, fill: "#64748b", "font-size": 10 })).textContent = f1(s.min);
  return svg;
}
function bandChart(labels, lo, mid, hi, color = "#2563eb", height = 220) {
  const W = 600, H = height, pad = 30; const s = scaleAll([...lo, ...mid, ...hi], W, H, pad);
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  if (!s) { svg.appendChild(svgEl("text", { x: 20, y: 30, fill: "#64748b", "font-size": 12 })).textContent = "No probabilistic data"; return svg; }
  const n = mid.length;
  const up = hi.map((v, i) => `${s.x(i, n)},${s.y(v)}`).join(" ");
  const dn = lo.map((v, i) => `${s.x(i, n)},${s.y(v)}`).reverse().join(" ");
  svg.appendChild(svgEl("polygon", { points: up + " " + dn, fill: color, opacity: 0.15 }));
  svg.appendChild(svgEl("polyline", { points: mid.map((v, i) => `${s.x(i, n)},${s.y(v)}`).join(" "), fill: "none", stroke: color, "stroke-width": 2 }));
  labels.forEach((L, i) => { if (i % Math.ceil(n / 7) === 0) { const t = svgEl("text", { x: s.x(i, n), y: H - 6, fill: "#64748b", "font-size": 9, "text-anchor": "middle" }); t.textContent = L; svg.appendChild(t); } });
  return svg;
}
function barChart(labels, values, color = "#2563eb", height = 200) {
  const W = 600, H = height, pad = 30; const s = scaleAll([0, ...values], W, H, pad);
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  if (!s) { svg.appendChild(svgEl("text", { x: 20, y: 30, fill: "#64748b", "font-size": 12 })).textContent = "No data"; return svg; }
  const n = values.length; const bw = ((W - 2 * pad) / n) * 0.6;
  values.forEach((v, i) => {
    const x = s.x(i, n) - bw / 2; const y = s.y(Math.max(v || 0, 0));
    svg.appendChild(svgEl("rect", { x, y, width: bw, height: Math.max(H - pad - y, 1), fill: color, rx: 2 }));
    const t = svgEl("text", { x: s.x(i, n), y: H - 6, fill: "#64748b", "font-size": 9, "text-anchor": "middle" }); t.textContent = labels[i]; svg.appendChild(t);
  });
  return svg;
}
function gauge(v01, label, color = "#16a34a") {
  const W = 140, H = 90, r = 55, cx = 70, cy = 78; const val = Math.max(0, Math.min(1, v01 || 0));
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  const arc = (a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  const [bx0, by0] = arc(Math.PI), [bx1, by1] = arc(Math.PI * 2);
  svg.appendChild(svgEl("path", { d: `M ${bx0} ${by0} A ${r} ${r} 0 0 1 ${bx1} ${by1}`, fill: "none", stroke: "#e3e8f0", "stroke-width": 10 }));
  const [x0, y0] = arc(Math.PI), [x1, y1] = arc(Math.PI * (1 + val));
  svg.appendChild(svgEl("path", { d: `M ${x0} ${y0} A ${r} ${r} 0 0 1 ${x1} ${y1}`, fill: "none", stroke: color, "stroke-width": 10 }));
  const t = svgEl("text", { x: cx, y: cy - 8, fill: "#0f172a", "font-size": 18, "text-anchor": "middle", "font-weight": 700 }); t.textContent = (val * 100).toFixed(0); svg.appendChild(t);
  const l = svgEl("text", { x: cx, y: cy + 8, fill: "#64748b", "font-size": 9, "text-anchor": "middle" }); l.textContent = label; svg.appendChild(l);
  return svg;
}
const legend = (items) => el("div", { className: "legend" }, items.map(([c, t]) => el("span", {}, [el("i", { style: `background:${c}` }), t])));

const predictFull = (h) => post(`/api/v1/predict/full?location=${state.location}&horizon_hours=${h}`).catch(() => null);
const tv = (f, task, key) => (f && f.tasks && f.tasks[task] ? f.tasks[task][key] : undefined);

async function renderOverview(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Overview"]));
  const [cur, hourly, daily, full, alerts, champs] = await Promise.all([
    safe(() => api(`/api/v1/weather/current/${state.location}`), null),
    safe(() => api(`/api/v1/weather/hourly/${state.location}`), null),
    safe(() => api(`/api/v1/weather/daily/${state.location}`), null),
    predictFull(24), safe(() => api("/api/v1/alerts"), []), safe(() => api("/api/v1/models/champions"), []),
  ]);
  if (cur) c.appendChild(el("div", { className: "hero" }, [
    el("div", { className: "icon" }, [conditionIcon(cur.weather_code)]),
    el("div", {}, [el("div", { className: "big" }, [`${f1(cur.temperature_2m)}°C`]), el("div", { className: "cond" }, ["Partly Cloudy"]), el("div", { className: "feels" }, [`Feels like ${f1(cur.apparent_temperature)}°C`])]),
    el("div", { className: "mini" }, [
      el("div", {}, [el("b", {}, [`${f0(cur.relative_humidity_2m)}%`]), el("span", {}, ["Humidity"])]),
      el("div", {}, [el("b", {}, [`${f1(cur.wind_speed_10m)}`]), el("span", {}, ["Wind km/h"])]),
      el("div", {}, [el("b", {}, [`${f0(cur.pressure_msl)}`]), el("span", {}, ["Pressure"])]),
      el("div", {}, [el("b", {}, [`${f1(cur.visibility)}`]), el("span", {}, ["Visibility"])]),
    ]),
  ]));
  else c.appendChild(empty("No observation data - run: atmosiq ingest"));
  const g = el("div", { className: "grid cols-3", style: "margin-top:16px" });
  if (hourly) g.appendChild(card("Temperature (°C)", el("div", {}, [lineChart(hourly.times.slice(0, 24).map((t) => t.slice(11, 16)), [{ color: "#dc2626", values: hourly.temperature_2m.slice(0, 24) }]), legend([["#dc2626", "°C"]])])));
  if (full) g.appendChild(card("Rain Probability (%)", el("div", {}, [barChart(HORIZONS.map((h) => h + "h"), HORIZONS.map(() => null), "#2563eb")]), "see Rainfall page for live values"));
  if (daily) g.appendChild(card("Precipitation (mm)", el("div", {}, [barChart(daily.dates, daily.precipitation_sum, "#2563eb"), legend([["#2563eb", "mm"]])])));
  c.appendChild(g);
  const g2 = el("div", { className: "grid cols-2", style: "margin-top:16px" });
  if (full && full.risk) g2.appendChild(card("Severe Weather Risk", el("div", {}, [
    el("div", { className: "risk-row" }, [el("span", {}, ["Heat"]), badge(full.risk.heat?.level || "normal", riskKind(full.risk.heat?.level))]),
    el("div", { className: "risk-row" }, [el("span", {}, ["Heavy rain"]), badge(full.risk.heavy_rain?.level || "minimal", riskKind(full.risk.heavy_rain?.level))]),
    el("div", { className: "risk-row" }, [el("span", {}, ["High wind"]), badge(full.risk.high_wind?.level || "minimal", riskKind(full.risk.high_wind?.level))]),
  ])));
  if (champs.length) g2.appendChild(card("Active Champions", table(["Task", "Horizon", "Model"], champs.slice(0, 6).map((m) => [m.task, m.horizon_hours + "h", el("span", { className: "model-tag" }, [m.model])]))));
  if (Array.isArray(alerts) && alerts.length) g2.appendChild(card("Alerts", table(["Severity", "Type", "Message"], alerts.slice(0, 4).map((a) => [badge(a.severity, a.severity === "CRITICAL" ? "danger" : a.severity === "WARNING" ? "warning" : "info"), a.alert_type, a.message]))));
  c.appendChild(g2);
}

async function renderCurrent(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Current Weather"]));
  const cur = await safe(() => api(`/api/v1/weather/current/${state.location}`), null);
  if (!cur) return c.appendChild(empty("No data - run: atmosiq ingest"));
  const g = el("div", { className: "grid cols-4" });
  [["Temperature", `${f1(cur.temperature_2m)}°C`], ["Feels Like", `${f1(cur.apparent_temperature)}°C`], ["Humidity", `${f0(cur.relative_humidity_2m)}%`], ["Wind", `${f1(cur.wind_speed_10m)} km/h`], ["Pressure", `${f0(cur.pressure_msl)} hPa`], ["Visibility", `${f1(cur.visibility)} m`]].forEach(([k, v]) => g.appendChild(card(k, el("div", { className: "stat-value" }, [v]))));
  c.appendChild(g);
}

async function renderHourly(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Hourly Forecast"]));
  const hourly = await safe(() => api(`/api/v1/weather/hourly/${state.location}`), null);
  if (hourly) c.appendChild(card("Recent 48h", el("div", {}, [
    lineChart(hourly.times.map((t) => t.slice(11, 16)), [{ color: "#dc2626", values: hourly.temperature_2m }, { color: "#2563eb", values: hourly.precipitation }]),
    legend([["#dc2626", "°C"], ["#2563eb", "mm"]]),
  ])));
  const hs = [1, 3, 6, 12, 24]; const temps = [], probs = [];
  for (const h of hs) { const f = await predictFull(h); temps.push(tv(f, "temperature", "prediction")); probs.push(tv(f, "rain_occurrence", "rain_probability") != null ? tv(f, "rain_occurrence", "rain_probability") * 100 : null); }
  const g = el("div", { className: "grid cols-2", style: "margin-top:16px" });
  g.appendChild(card("Next 24h ML Temperature", el("div", {}, [lineChart(hs.map((h) => h + "h"), [{ color: "#dc2626", values: temps }])]), "champion model"));
  g.appendChild(card("Rain Probability", el("div", {}, [barChart(hs.map((h) => h + "h"), probs, "#2563eb")])));
  c.appendChild(g);
}

async function renderDaily(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Daily Forecast"]));
  const daily = await safe(() => api(`/api/v1/weather/daily/${state.location}`), null);
  if (!daily) return c.appendChild(empty("No data - run: atmosiq ingest"));
  c.appendChild(card("7-Day", table(["Date", "Max", "Min", "Precip", "Wind Max"], daily.dates.map((d, i) => [d, `${f1(daily.temperature_max[i])}°`, `${f1(daily.temperature_min[i])}°`, `${f1(daily.precipitation_sum[i])} mm`, `${f1(daily.wind_speed_max[i])}`]))));
  c.appendChild(el("div", { style: "margin-top:16px" }, [card("Temperature Trend", el("div", {}, [lineChart(daily.dates, [{ color: "#dc2626", values: daily.temperature_max }, { color: "#2563eb", values: daily.temperature_min }]), legend([["#dc2626", "Max"], ["#2563eb", "Min"]])]))]));
}

async function renderRainfall(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Rainfall"]));
  const hs = [1, 3, 6, 12, 24, 48, 72]; const probs = [], amts = [], intens = [];
  for (const h of hs) { const f = await predictFull(h); probs.push(tv(f, "rain_occurrence", "rain_probability") != null ? tv(f, "rain_occurrence", "rain_probability") * 100 : null); amts.push(tv(f, "precipitation_amount", "prediction")); intens.push(f ? f.rain_intensity : null); }
  const g = el("div", { className: "grid cols-2" });
  g.appendChild(card("Rainfall (mm)", el("div", {}, [barChart(hs.map((h) => h + "h"), amts, "#2563eb")])));
  g.appendChild(card("Rain Probability (%)", el("div", {}, [lineChart(hs.map((h) => h + "h"), [{ color: "#16a34a", values: probs }])])));
  c.appendChild(g);
  c.appendChild(el("div", { style: "margin-top:16px" }, [card("Intensity", table(["Horizon", "Amount", "Category"], hs.map((h, i) => [h + "h", `${f1(amts[i])} mm`, badge(intens[i] || "-", intens[i] === "no_rain" ? "muted" : intens[i] === "light" ? "info" : intens[i] === "moderate" ? "warning" : "danger")])))]));
}

async function renderWind(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Wind"]));
  const hs = [1, 6, 24, 48]; const rows = [];
  for (const h of hs) { const f = await predictFull(h); rows.push([h + "h", f1(tv(f, "wind_speed", "prediction")), f1(tv(f, "wind_gusts", "prediction")), tv(f, "wind_direction", "direction") || "-"]); }
  c.appendChild(card("Wind by Horizon", table(["Horizon", "Speed km/h", "Gust km/h", "Direction"], rows)));
}

async function renderMap(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Weather Map - Live Stations"]));
  const locs = await safe(() => api("/api/v1/locations"), []);
  const W = 700, H = 460; const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  svg.appendChild(svgEl("rect", { x: 0, y: 0, width: W, height: H, fill: "#eef2f7", rx: 14 }));
  const proj = (lat, lon) => [((lon - 68) / (97 - 68)) * (W - 80) + 40, (1 - (lat - 6) / (36 - 6)) * (H - 80) + 40];
  for (const L of locs) {
    const cur = await safe(() => api(`/api/v1/weather/current/${L.id}`), null);
    const t = cur ? cur.temperature_2m : null; const [x, y] = proj(L.latitude, L.longitude);
    svg.appendChild(svgEl("circle", { cx: x, cy: y, r: 8, fill: t != null ? tempColor(t) : "#94a3b8" }));
    const txt = svgEl("text", { x: x + 11, y: y + 4, fill: "#0f172a", "font-size": 10 }); txt.textContent = `${L.name} ${t != null ? f1(t) + "C" : ""}`; svg.appendChild(txt);
  }
  c.appendChild(card("Live observed temperature", svg));
}

async function renderHistorical(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Historical Weather"]));
  const hourly = await safe(() => api(`/api/v1/weather/hourly/${state.location}`), null);
  const daily = await safe(() => api(`/api/v1/weather/daily/${state.location}`), null);
  if (daily) {
    const temps = daily.temperature_max.filter((v) => v != null);
    const rain = daily.precipitation_sum.filter((v) => v != null);
    const g = el("div", { className: "grid cols-4" });
    g.appendChild(card("Avg Max", el("div", { className: "stat-value" }, [`${f1(temps.reduce((a, b) => a + b, 0) / Math.max(temps.length, 1))}°C`])));
    g.appendChild(card("Max", el("div", { className: "stat-value" }, [`${f1(Math.max(...temps))}°C`])));
    g.appendChild(card("Min", el("div", { className: "stat-value" }, [`${f1(Math.min(...daily.temperature_min.filter((v) => v != null)))}°C`])));
    g.appendChild(card("Total Rain", el("div", { className: "stat-value" }, [`${f1(rain.reduce((a, b) => a + b, 0))} mm`])));
    c.appendChild(g);
  }
  if (hourly) c.appendChild(el("div", { style: "margin-top:16px" }, [card("Observed Temperature", el("div", {}, [lineChart(hourly.times.map((t) => t.slice(11, 16)), [{ color: "#dc2626", values: hourly.temperature_2m }])]))]));
}

async function renderForecast(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["ML Forecast"]));
  const pills = el("div", { className: "pills" });
  HORIZONS.forEach((h) => { const b = el("button", { className: h === state.horizon ? "on" : "" }, [h + "h"]); b.onclick = () => { state.horizon = h; router(); }; pills.appendChild(b); });
  c.appendChild(pills);
  const lo = [], mid = [], hi = []; let full = null;
  for (const h of HORIZONS) { const f = await predictFull(h); if (h === state.horizon) full = f; lo.push(tv(f, "temperature", "p10")); mid.push(tv(f, "temperature", "p50") ?? tv(f, "temperature", "prediction")); hi.push(tv(f, "temperature", "p90")); }
  c.appendChild(card("Temperature P10/P50/P90", el("div", {}, [bandChart(HORIZONS.map((h) => h + "h"), lo, mid, hi), legend([["#2563eb", "P50"], ["rgba(37,99,235,.3)", "P10-P90"]])]), "probabilistic champion output"));
  if (!full) return c.appendChild(empty("No trained champion yet - run: atmosiq train"));
  const t = full.tasks || {};
  const g = el("div", { className: "grid cols-3", style: "margin-top:16px" });
  const add = (title, val, sub, model) => g.appendChild(card(title, el("div", {}, [el("div", { className: "stat-value" }, [val]), el("div", { className: "stat-sub" }, [sub || ""]), model ? el("div", { style: "margin-top:6px" }, [el("span", { className: "model-tag" }, [model])]) : el("span", {})]));
  add("Temperature", `${f1(t.temperature?.prediction)}°C`, `P10 ${f1(t.temperature?.p10)} / P90 ${f1(t.temperature?.p90)}`, t.temperature?.model);
  add("Rain", pct(t.rain_occurrence?.rain_probability), `${f1(t.precipitation_amount?.prediction)} mm - ${full.rain_intensity || "-"}`, t.rain_occurrence?.model);
  add("Wind", `${f1(t.wind_speed?.prediction)} km/h`, `Gust ${f1(t.wind_gusts?.prediction)} - ${t.wind_direction?.direction || "-"}`, t.wind_speed?.model);
  add("Humidity", `${f0(t.humidity?.prediction)}%`, "", t.humidity?.model);
  add("Pressure", `${f0(t.pressure?.prediction)} hPa`, "", t.pressure?.model);
  add("Condition", t.weather_condition?.condition || "-", "", t.weather_condition?.model);
  c.appendChild(g);
}

async function renderAccuracy(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Forecast Accuracy"]));
  const [ver, board] = await Promise.all([safe(() => api("/api/v1/verification"), []), safe(() => api("/api/v1/models/leaderboard"), [])]);
  const skill = board.filter((r) => r.task === "temperature" && r.skill_vs_persistence != null);
  if (skill.length) { const g = el("div", { className: "grid cols-4" }); skill.slice(0, 4).forEach((r) => g.appendChild(card(r.model, gauge(r.skill_vs_persistence, "skill")))); c.appendChild(g); }
  if (ver.length) c.appendChild(el("div", { style: "margin-top:16px" }, [card("Verified vs Actuals", table(["Task", "Horizon", "N", "MAE", "RMSE", "Bias"], ver.map((v) => [v.task, v.horizon_hours + "h", v.n, f1(v.mae), f1(v.rmse), f1(v.bias)])))]));
  else c.appendChild(empty("No verifications yet - run: atmosiq monitor after predictions age past their valid_time"));
}

async function renderModels(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Models"]));
  const [board, champs] = await Promise.all([safe(() => api("/api/v1/models/leaderboard"), []), safe(() => api("/api/v1/models/champions"), [])]);
  if (champs.length) c.appendChild(card("Champions (serving)", table(["Task", "Horizon", "Model", "Version"], champs.map((m) => [m.task, m.horizon_hours + "h", el("span", { className: "model-tag" }, [m.model]), m.version.slice(0, 12)]))));
  if (board.length) c.appendChild(el("div", { style: "margin-top:16px" }, [card("Leaderboard (test set)", table(["Model", "Task", "Hor", "MAE", "RMSE", "Skill", "PR-AUC", "Status"], board.map((r) => [r.model, r.task, r.horizon, r.mae != null ? r.mae.toFixed(3) : "-", r.rmse != null ? r.rmse.toFixed(3) : "-", r.skill_vs_persistence != null ? r.skill_vs_persistence.toFixed(2) : "-", r.pr_auc != null ? r.pr_auc.toFixed(2) : "-", badge(r.skill_vs_persistence > 0 ? "Champion" : "Challenger", r.skill_vs_persistence > 0 ? "success" : "warning")])))]));
  else c.appendChild(empty("No leaderboard yet - run: atmosiq train"));
}

async function renderModelDetails(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Model Details"]));
  const models = await safe(() => api("/api/v1/models"), []);
  if (!models.length) return c.appendChild(empty("No models yet - run: atmosiq train"));
  const sel = el("select", {}); models.slice(0, 60).forEach((m) => sel.appendChild(el("option", { value: m.id }, [`${m.model_name} | ${m.task} | ${m.horizon_hours}h | ${m.stage}`]));
  c.appendChild(sel);
  const detail = el("div", { style: "margin-top:16px" });
  c.appendChild(detail);
  async function show() {
    const id = sel.value; const m = models.find((x) => x.id === id);
    detail.innerHTML = "";
    detail.appendChild(card("Registry record", table(["Field", "Value"], [["Model", m.model_name], ["Task", m.task], ["Horizon", m.horizon_hours + "h"], ["Stage", badge(m.stage, m.stage === "Champion" ? "success" : "muted")], ["Version", m.id]])));
    const board = await safe(() => api(`/api/v1/models/leaderboard?task=${m.task}&horizon=${m.horizon_hours}`), []);
    const row = board.find((r) => r.model === m.model_name);
    if (row) detail.appendChild(el("div", { style: "margin-top:16px" }, [card("Test-set performance", table(["MAE", "RMSE", "Skill", "PR-AUC"], [[row.mae != null ? row.mae.toFixed(3) : "-", row.rmse != null ? row.rmse.toFixed(3) : "-", row.skill_vs_persistence != null ? row.skill_vs_persistence.toFixed(2) : "-", row.pr_auc != null ? row.pr_auc.toFixed(2) : "-"]]))]));
  }
  sel.onchange = show; show();
}

async function renderDrift(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Drift Monitoring"]));
  const ev = await safe(() => api("/api/v1/monitoring/drift"), []);
  if (!ev.length) return c.appendChild(empty("No drift events - run: atmosiq monitor"));
  c.appendChild(card("PSI / KS", table(["Feature", "PSI", "KS", "p-value", "Threshold", "Detected", "Time"], ev.map((e) => [e.feature, e.psi, e.ks_statistic, e.p_value, e.threshold, badge(e.detected ? "yes" : "no", e.detected ? "danger" : "success"), e.timestamp]))));
}

async function renderAlerts(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Alerts"]));
  const a = await safe(() => api("/api/v1/alerts"), []);
  if (!a.length) return c.appendChild(empty("No alerts"));
  c.appendChild(card("Alerts", table(["Severity", "Type", "Scope", "Message", "Status", "Created"], a.map((x) => [badge(x.severity, x.severity === "CRITICAL" ? "danger" : x.severity === "WARNING" ? "warning" : "info"), x.alert_type, x.scope, x.message, x.status, x.created_at]))));
}

async function renderExplorer(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Data Explorer"]));
  const hourly = await safe(() => api(`/api/v1/weather/hourly/${state.location}`), null);
  if (!hourly) return c.appendChild(empty("No data - run: atmosiq ingest"));
  const btn = el("button", { className: "btn" }, ["Export CSV"]);
  btn.onclick = () => {
    const rows = [hourly.times, hourly.temperature_2m, hourly.precipitation, hourly.wind_speed_10m];
    let csv = "time,temperature,precipitation,wind\n";
    hourly.times.forEach((t, i) => { csv += `${t},${hourly.temperature_2m[i]},${hourly.precipitation[i]},${hourly.wind_speed_10m[i]}\n`; });
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" })); a.download = "atmosiq_data.csv"; a.click();
  };
  c.appendChild(btn);
  c.appendChild(el("div", { style: "margin-top:16px" }, [card("Recent observations", table(["Time", "Temp", "Precip", "Rain%", "Wind"], hourly.times.map((t, i) => [t, f1(hourly.temperature_2m[i]), f1(hourly.precipitation[i]), f0(hourly.precipitation_probability[i]), f1(hourly.wind_speed_10m[i])])))]));
}

async function renderReports(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Reports"]));
  const [sum, ver, board, drift] = await Promise.all([safe(() => api("/api/v1/monitoring/summary"), null), safe(() => api("/api/v1/verification"), []), safe(() => api("/api/v1/models/leaderboard"), []), safe(() => api("/api/v1/monitoring/drift"), [])]);
  const g = el("div", { className: "grid cols-4" });
  g.appendChild(card("Forecast Accuracy", el("div", { className: "stat-value" }, [String(ver.length)]), "verified rows"));
  g.appendChild(card("Models Evaluated", el("div", { className: "stat-value" }, [String(board.length)]), "leaderboard rows"));
  g.appendChild(card("Drift Events", el("div", { className: "stat-value" }, [String(drift.length)]), "PSI/KS checks"));
  g.appendChild(card("Champions", el("div", { className: "stat-value" }, [sum ? String(sum.champion_count) : "0"]), "serving now"));
  c.appendChild(g);
  c.appendChild(el("div", { className: "sub", style: "margin-top:12px" }, ["Full artifacts live in artifacts/<ts>/model_evaluation/ (leaderboard.json, quality_gate.json, error_analysis.json)."]));
}

async function renderHealth(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["System Health"]));
  const live = await safe(() => api("/health/live"), null);
  const ready = await safe(() => api("/health/ready"), null);
  const sum = await safe(() => api("/api/v1/monitoring/summary"), null);
  const g = el("div", { className: "grid cols-4" });
  g.appendChild(card("API", el("div", { className: "stat-value" }, [live ? live.status : "down"])));
  g.appendChild(card("DB", el("div", { className: "stat-value" }, [ready ? ready.status : "down"])));
  if (sum) { g.appendChild(card("Champions", el("div", { className: "stat-value" }, [String(sum.champion_count)]))); g.appendChild(card("Open Alerts", el("div", { className: "stat-value" }, [String(sum.active_alerts)]))); }
  c.appendChild(g);
}

function renderSettings(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Settings"]));
  c.appendChild(card("Units & Format", el("div", {}, [
    el("div", { className: "kv" }, [el("span", { className: "k" }, ["Temperature"]), el("span", {}, ["°C (Celsius)"])]),
    el("div", { className: "kv" }, [el("span", { className: "k" }, ["Wind"]), el("span", {}, ["km/h"])]),
    el("div", { className: "kv" }, [el("span", { className: "k" }, ["Pressure"]), el("span", {}, ["hPa"])]),
    el("div", { className: "kv" }, [el("span", { className: "k" }, ["Rain"]), el("span", {}, ["mm"])]),
  ]), "Server-side business rules live in config/atmosiq.yaml (ranges, risk bands, quality gate, drift thresholds). Edit there and retrain.");
}

function buildSidebar() {
  const nav = document.getElementById("sidebar"); nav.innerHTML = "";
  for (const p of PAGES) {
    if (p.group) nav.appendChild(el("div", { className: "group" }, [p.group]));
    nav.appendChild(el("a", { href: `#${p.route}`, "data-route": p.route }, [el("span", {}, [p.icon]), p.title]));
  }
}
function highlight() {
  const path = location.hash.replace(/^#/, "") || "overview";
  document.querySelectorAll("#sidebar a").forEach((a) => a.classList.toggle("active", a.getAttribute("data-route") === path));
}
async function initTopbar() {
  const locSel = document.getElementById("locSelect");
  const locs = await safe(() => api("/api/v1/locations"), []);
  locSel.innerHTML = ""; locs.forEach((l) => locSel.appendChild(el("option", { value: l.id }, [l.name])));
  if (locs.length) state.location = locs[0].id;
  locSel.onchange = () => { state.location = locSel.value; router(); };
  document.getElementById("refreshBtn").onclick = () => router();
  document.getElementById("dateLabel").textContent = new Date().toDateString();
}
async function router() {
  const path = location.hash.replace(/^#/, "") || "overview";
  const page = PAGES.find((p) => p.route === path) || PAGES[0];
  const content = document.getElementById("content"); content.innerHTML = ""; highlight();
  try { await page.render(content); } catch (e) { content.appendChild(card("Error", empty(String(e)))); }
}
buildSidebar(); initTopbar();
window.addEventListener("hashchange", router); router();
'''

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))

print(f"Part 11 (production) written: {len(W)} files.")
