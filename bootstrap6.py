# bootstrap6.py -> run: python bootstrap6.py  (upgrades frontend/)
import os

W = {}

W["frontend/index.html"] = r'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AtmosIQ - Weather ML Platform</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header id="topbar">
    <div class="brand">Atmos<span>IQ</span></div>
    <select id="locSelect"></select>
    <select id="horizonSelect"></select>
    <button id="refreshBtn" title="Refresh">&#8635;</button>
    <div class="spacer"></div>
    <span id="updatedLabel" class="muted"></span>
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
:root {
  --bg: #0b1220;
  --panel: #121c30;
  --panel2: #0f1828;
  --border: #22304a;
  --text: #e6edf7;
  --muted: #8fa3bf;
  --accent: #3b82f6;
  --accent2: #38bdf8;
  --success: #4ade80;
  --warning: #facc15;
  --danger: #f87171;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Inter", "Segoe UI", system-ui, sans-serif; background: var(--bg); color: var(--text); }
#topbar { display: flex; align-items: center; gap: 12px; padding: 12px 20px; background: var(--panel2); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 10; }
.brand { font-size: 20px; font-weight: 700; color: var(--text); margin-right: 12px; }
.brand span { color: var(--accent2); }
#topbar select, #topbar button { background: var(--panel); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 7px 10px; font-size: 13px; }
#topbar button { cursor: pointer; }
.spacer { flex: 1; }
.muted { color: var(--muted); font-size: 12px; }
.layout { display: flex; min-height: calc(100vh - 53px); }
#sidebar { width: 230px; background: var(--panel2); border-right: 1px solid var(--border); padding: 16px 10px; }
#sidebar .group { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .06em; margin: 14px 8px 6px; }
#sidebar a { display: block; color: var(--muted); text-decoration: none; padding: 9px 12px; border-radius: 8px; font-size: 13.5px; margin-bottom: 2px; }
#sidebar a:hover { background: var(--panel); color: var(--text); }
#sidebar a.active { background: var(--accent); color: #fff; }
#content { flex: 1; padding: 22px; overflow-y: auto; }
.page-title { font-size: 22px; margin-bottom: 16px; }
.grid { display: grid; gap: 16px; }
.grid.cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid.cols-4 { grid-template-columns: repeat(4, 1fr); }
.grid.cols-2 { grid-template-columns: repeat(2, 1fr); }
@media (max-width: 1100px) { .grid.cols-3, .grid.cols-4 { grid-template-columns: repeat(2, 1fr); } }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 18px; }
.card h3 { font-size: 14px; color: var(--accent2); margin-bottom: 12px; font-weight: 600; }
.stat-label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .05em; }
.stat-value { font-size: 26px; font-weight: 700; margin-top: 2px; }
.stat-sub { color: var(--muted); font-size: 12px; margin-top: 2px; }
.big-temp { font-size: 44px; font-weight: 700; }
.kv { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px dashed var(--border); font-size: 13px; }
.kv:last-child { border-bottom: none; }
.kv .k { color: var(--muted); }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px 10px; border-bottom: 1px solid var(--border); text-align: left; font-size: 13px; }
th { color: var(--muted); font-weight: 500; font-size: 12px; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 600; }
.badge-success { background: rgba(74,222,128,.15); color: var(--success); }
.badge-warning { background: rgba(250,204,21,.15); color: var(--warning); }
.badge-danger { background: rgba(248,113,113,.15); color: var(--danger); }
.badge-info { background: rgba(56,189,248,.15); color: var(--accent2); }
.badge-muted { background: rgba(143,163,191,.15); color: var(--muted); }
.pills { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.pills button { background: var(--panel2); color: var(--muted); border: 1px solid var(--border); border-radius: 999px; padding: 5px 12px; font-size: 12px; cursor: pointer; }
.pills button.on { background: var(--accent); color: #fff; border-color: var(--accent); }
svg { display: block; width: 100%; height: auto; }
.legend { display: flex; gap: 14px; margin-top: 8px; flex-wrap: wrap; }
.legend span { font-size: 12px; color: var(--muted); display: inline-flex; align-items: center; gap: 6px; }
.legend i { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
.icon { font-size: 40px; }
.risk-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px dashed var(--border); }
.risk-row:last-child { border-bottom: none; }
'''

W["frontend/app.js"] = r'''
const API_BASE = "";
const state = { location: "kavali", horizon: 24 };

const PAGES = [
  { group: "", route: "overview", title: "Overview", render: renderOverview },
  { group: "Forecast", route: "current", title: "Current Weather", render: renderCurrent },
  { group: "", route: "hourly", title: "Hourly Forecast", render: renderHourly },
  { group: "", route: "daily", title: "Daily Forecast", render: renderDaily },
  { group: "", route: "rainfall", title: "Rainfall", render: renderRainfall },
  { group: "", route: "wind", title: "Wind", render: renderWind },
  { group: "", route: "map", title: "Weather Map", render: renderMap },
  { group: "ML Operations", route: "forecast", title: "ML Forecast", render: renderForecast },
  { group: "", route: "models", title: "Models", render: renderModels },
  { group: "Analytics", route: "accuracy", title: "Forecast Accuracy", render: renderAccuracy },
  { group: "", route: "drift", title: "Drift Monitoring", render: renderDrift },
  { group: "", route: "alerts", title: "Alerts", render: renderAlerts },
  { group: "System", route: "health", title: "System Health", render: renderHealth },
];

async function api(path, method = "GET") {
  const res = await fetch(API_BASE + path, { method });
  if (!res.ok) throw new Error(`API ${path} -> ${res.status}`);
  return res.json();
}
const post = (path) => api(path, "POST");

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "className") node.className = v;
    else if (k === "innerHTML") node.innerHTML = v;
    else node.setAttribute(k, v);
  }
  for (const c of children) node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  return node;
}
const card = (title, body) => el("div", { className: "card" }, [el("h3", {}, [title]), body]);
const f1 = (v) => (v == null ? "-" : Number(v).toFixed(1));
const f0 = (v) => (v == null ? "-" : Math.round(Number(v)));
const badge = (text, kind = "info") => el("span", { className: `badge badge-${kind}` }, [String(text)]);
function table(headers, rows) {
  return el("table", {}, [
    el("thead", {}, [el("tr", {}, headers.map((h) => el("th", {}, [h])))]),
    el("tbody", {}, rows.map((r) => el("tr", {}, r.map((c) => el("td", {}, [typeof c === "string" || typeof c === "number" ? String(c) : c]))))),
  ]);
}
function conditionIcon(code) {
  if (code == null) return "☁️";
  code = Number(code);
  if (code === 0) return "☀️";
  if (code <= 2) return "🌤️";
  if (code === 3) return "☁️";
  if (code === 45 || code === 48) return "🌫️";
  if (code <= 67) return "🌧️";
  if (code <= 77 || code === 85 || code === 86) return "❄️";
  if (code <= 82) return "🌧️";
  if (code >= 95) return "⛈️";
  return "☁️";
}
function tempColor(t) {
  const stops = [[-5, "#38bdf8"], [10, "#4ade80"], [20, "#facc15"], [30, "#fb923c"], [40, "#f87171"]];
  for (let i = stops.length - 1; i >= 0; i--) if (t >= stops[i][0]) return stops[i][1];
  return stops[0][1];
}

function svgEl(tag, attrs) {
  const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
}
function scale(vals, W, H, pad) {
  const nums = vals.filter((v) => v != null && !isNaN(v));
  const min = Math.min(...nums), max = Math.max(...nums);
  const x = (i, n) => pad + (i * (W - 2 * pad)) / Math.max(n - 1, 1);
  const y = (v) => H - pad - ((v - min) / Math.max(max - min, 1e-9)) * (H - 2 * pad);
  return { x, y, min, max };
}
function lineChart(labels, series, height = 200) {
  const W = 600, H = height, pad = 30;
  const all = series.flatMap((s) => s.values);
  const s = scale(all, W, H, pad);
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  for (const ser of series) {
    const pts = ser.values.map((v, i) => (v == null ? null : `${s.x(i, ser.values.length)},${s.y(v)}`)).filter(Boolean).join(" ");
    svg.appendChild(svgEl("polyline", { points: pts, fill: "none", stroke: ser.color, "stroke-width": 2 }));
  }
  svg.appendChild(svgEl("text", { x: pad, y: 14, fill: "#8fa3bf", "font-size": 10 })).textContent = f1(s.max);
  svg.appendChild(svgEl("text", { x: pad, y: H - 8, fill: "#8fa3bf", "font-size": 10 })).textContent = f1(s.min);
  svg.appendChild(svgEl("text", { x: pad, y: H - 8, fill: "#8fa3bf", "font-size": 10 })).textContent = f1(s.min);
  return svg;
}
function bandChart(labels, lo, mid, hi, color = "#3b82f6", height = 220) {
  const W = 600, H = height, pad = 30;
  const s = scale([...lo, ...mid, ...hi], W, H, pad);
  const n = mid.length;
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  const up = hi.map((v, i) => `${s.x(i, n)},${s.y(v)}`).join(" ");
  const dn = [...lo].reverse().map((v, i) => `${s.x(n - 1 - i, n)},${s.y(v)}`).join(" ");
  svg.appendChild(svgEl("polygon", { points: up + " " + dn, fill: color, opacity: 0.18 }));
  svg.appendChild(svgEl("polyline", { points: mid.map((v, i) => `${s.x(i, n)},${s.y(v)}`).join(" "), fill: "none", stroke: color, "stroke-width": 2 }));
  return svg;
}
function barChart(labels, values, color = "#3b82f6", height = 200) {
  const W = 600, H = height, pad = 30;
  const s = scale([0, ...values], W, H, pad);
  const n = values.length;
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  const bw = ((W - 2 * pad) / n) * 0.6;
  values.forEach((v, i) => {
    const x = s.x(i, n) - bw / 2;
    const y = s.y(Math.max(v, 0));
    svg.appendChild(svgEl("rect", { x, y, width: bw, height: Math.max(H - pad - y, 1), fill: color, rx: 2 }));
  });
  return svg;
}
function legend(items) {
  return el("div", { className: "legend" }, items.map(([c, t]) => el("span", {}, [el("i", { style: `background:${c}` }), t])));
}

async function renderOverview(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Overview"]));
  const [current, hourly, daily, full] = await Promise.all([
    api(`/api/v1/weather/current/${state.location}`),
    api(`/api/v1/weather/hourly/${state.location}`),
    api(`/api/v1/weather/daily/${state.location}`),
    post(`/api/v1/predict/full?location=${state.location}&horizon_hours=24`).catch(() => null),
  ]);
  const top = el("div", { className: "grid cols-3" });
  top.appendChild(card("Current Weather", el("div", {}, [
    el("div", { style: "display:flex;align-items:center;gap:14px" }, [
      el("div", { className: "icon" }, [conditionIcon(current.weather_code)]),
      el("div", {}, [el("div", { className: "big-temp" }, [`${f1(current.temperature_2m)}°C`]), el("div", { className: "stat-sub" }, [`Feels like ${f1(current.apparent_temperature)}°C`])]),
    ]),
    el("div", { style: "margin-top:10px" }, [
      el("div", { className: "kv" }, [el("span", { className: "k" }, ["Humidity"]), el("span", {}, [`${f0(current.relative_humidity_2m)}%`])]),
      el("div", { className: "kv" }, [el("span", { className: "k" }, ["Wind"]), el("span", {}, [`${f1(current.wind_speed_10m)} km/h`])]),
      el("div", { className: "kv" }, [el("span", { className: "k" }, ["Pressure"]), el("span", {}, [`${f0(current.pressure_msl)} hPa`])]),
      el("div", { className: "kv" }, [el("span", { className: "k" }, ["Visibility"]), el("span", {}, [`${f1(current.visibility)} m`])]),
    ]),
  ])));
  const hLabels = hourly.times.slice(0, 12).map((t) => t.slice(11, 16));
  top.appendChild(card("Hourly Temperature", el("div", {}, [
    lineChart(hLabels, [{ name: "temp", color: "#fb923c", values: hourly.temperature_2m.slice(0, 12) }]),
    legend([["#fb923c", "°C"]]),
  ])));
  top.appendChild(card("7-Day Rainfall", el("div", {}, [
    barChart(daily.dates, daily.precipitation_sum, "#3b82f6"),
    legend([["#3b82f6", "mm"]]),
  ])));
  c.appendChild(top);

  if (full) {
    const t = full.tasks || {};
    const mid = el("div", { className: "grid cols-3", style: "margin-top:16px" });
    const temp = t.temperature || {};
    mid.appendChild(card("ML Temperature +24h (P10/P50/P90)", el("div", {}, [
      el("div", { className: "stat-value" }, [`${f1(temp.prediction)}°C`]),
      el("div", { className: "stat-sub" }, [`P10 ${f1(temp.p10)} / P90 ${f1(temp.p90)}`]),
    ])));
    const rain = t.rain_occurrence || {};
    const amt = t.precipitation_amount || {};
    mid.appendChild(card("Rain +24h", el("div", {}, [
      el("div", { className: "stat-value" }, [`${f0((rain.rain_probability ?? 0) * 100)}%`]),
      el("div", { className: "stat-sub" }, [`${f1(amt.prediction)} mm - ${full.rain_intensity || "-"}`]),
    ])));
    const risk = full.risk || {};
    mid.appendChild(card("Risk Signals", el("div", {}, [
      el("div", { className: "risk-row" }, [el("span", {}, ["Heat"]), badge((risk.heat || {}).level || "-", "warning")]),
      el("div", { className: "risk-row" }, [el("span", {}, ["Heavy rain"]), badge((risk.heavy_rain || {}).level || "-", "danger")]),
      el("div", { className: "risk-row" }, [el("span", {}, ["High wind"]), badge((risk.high_wind || {}).level || "-", "info")]),
    ])));
    c.appendChild(mid);
  }
}

async function renderCurrent(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Current Weather"]));
  const current = await api(`/api/v1/weather/current/${state.location}`);
  const g = el("div", { className: "grid cols-4" });
  const items = [
    ["Temperature", `${f1(current.temperature_2m)}°C`], ["Feels Like", `${f1(current.apparent_temperature)}°C`],
    ["Humidity", `${f0(current.relative_humidity_2m)}%`], ["Wind", `${f1(current.wind_speed_10m)} km/h`],
    ["Pressure", `${f0(current.pressure_msl)} hPa`], ["Visibility", `${f1(current.visibility)} m`],
  ];
  items.forEach(([k, v]) => g.appendChild(card(k, el("div", { className: "stat-value" }, [v]))));
  c.appendChild(g);
}

async function renderHourly(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Hourly Forecast"]));
  const hourly = await api(`/api/v1/weather/hourly/${state.location}`);
  const labels = hourly.times.map((t) => t.slice(11, 16));
  c.appendChild(card("Temperature / Precip", el("div", {}, [
    lineChart(labels, [
      { name: "temp", color: "#fb923c", values: hourly.temperature_2m },
      { name: "precip", color: "#3b82f6", values: hourly.precipitation },
    ]),
    legend([["#fb923c", "°C"], ["#3b82f6", "mm"]]),
  ])));
  c.appendChild(card("Table", table(["Time", "Temp C", "Precip mm", "Rain %", "Wind"], hourly.times.map((t, i) => [t, f1(hourly.temperature_2m[i]), f1(hourly.precipitation[i]), f0(hourly.precipitation_probability[i]), f1(hourly.wind_speed_10m[i])]))));
}

async function renderDaily(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Daily Forecast"]));
  const daily = await api(`/api/v1/weather/daily/${state.location}`);
  c.appendChild(card("7-Day", table(["Date", "Max C", "Min C", "Precip mm", "Wind Max"], daily.dates.map((d, i) => [d, f1(daily.temperature_max[i]), f1(daily.temperature_min[i]), f1(daily.precipitation_sum[i]), f1(daily.wind_speed_max[i])]))));
}

async function renderRainfall(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Rainfall"]));
  const horizons = [1, 3, 6, 12, 24];
  const results = await Promise.all(horizons.map((h) => post(`/api/v1/predict/full?location=${state.location}&horizon_hours=${h}`).catch(() => null)));
  const probs = [], amts = [];
  results.forEach((r, i) => {
    const t = (r && r.tasks) || {};
    probs.push(((t.rain_occurrence || {}).rain_probability ?? 0) * 100);
    amts.push((t.precipitation_amount || {}).prediction ?? 0);
  });
  const g = el("div", { className: "grid cols-2" });
  g.appendChild(card("Rain Probability by Horizon", el("div", {}, [barChart(horizons.map((h) => h + "h"), probs, "#38bdf8"), legend([["#38bdf8", "%"]])])));
  g.appendChild(card("Rainfall Amount by Horizon", el("div", {}, [barChart(horizons.map((h) => h + "h"), amts, "#3b82f6"), legend([["#3b82f6", "mm"]])])));
  c.appendChild(g);
  const last = results[results.length - 1];
  if (last) c.appendChild(card("Intensity", el("div", { className: "stat-value" }, [last.rain_intensity || "-"])));
}

async function renderWind(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Wind"]));
  const horizons = [1, 6, 24, 48];
  const rows = [];
  for (const h of horizons) {
    const r = await post(`/api/v1/predict/full?location=${state.location}&horizon_hours=${h}`).catch(() => null);
    const t = (r && r.tasks) || {};
    rows.push([h + "h", f1((t.wind_speed || {}).prediction), f1((t.wind_gusts || {}).prediction), (t.wind_direction || {}).direction || "-"]);
  }
  c.appendChild(card("Wind by Horizon", table(["Horizon", "Speed km/h", "Gust km/h", "Direction"], rows)));
}

async function renderMap(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Weather Map"]));
  const locations = await api("/api/v1/locations");
  const W = 700, H = 420;
  const svg = svgEl("svg", { viewBox: `0 0 ${W} ${H}` });
  svg.appendChild(svgEl("rect", { x: 0, y: 0, width: W, height: H, fill: "#0f1828", rx: 12 }));
  const proj = (lat, lon) => [((lon - 68) / (98 - 68)) * (W - 60) + 30, (1 - (lat - 6) / (38 - 6)) * (H - 60) + 30];
  for (const loc of locations) {
    const cur = await api(`/api/v1/weather/current/${loc.id}`).catch(() => null);
    const [x, y] = proj(loc.latitude, loc.longitude);
    const t = cur ? cur.temperature_2m : 20;
    svg.appendChild(svgEl("circle", { cx: x, cy: y, r: 10, fill: tempColor(t), opacity: 0.9 }));
    svg.appendChild(svgEl("text", { x: x + 14, y: y + 4, fill: "#e6edf7", "font-size": 12 })).textContent = `${loc.name} ${f1(t)}C`;
  }
  c.appendChild(card("Live Station Temperatures", svg));
  c.appendChild(el("div", { className: "muted", style: "margin-top:8px" }, ["Markers colored by live observed temperature (blue cold -> red hot)."]));
}

async function renderForecast(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["ML Forecast"]));
  const pills = el("div", { className: "pills" });
  [1, 3, 6, 12, 24, 48, 72].forEach((h) => {
    const b = el("button", { className: h === state.horizon ? "on" : "" }, [h + "h"]);
    b.onclick = () => { state.horizon = h; router(); };
    pills.appendChild(b);
  });
  c.appendChild(pills);
  const full = await post(`/api/v1/predict/full?location=${state.location}&horizon_hours=${state.horizon}`);
  const t = full.tasks || {};
  const g = el("div", { className: "grid cols-3" });
  const add = (title, body) => g.appendChild(card(title, body));
  const temp = t.temperature || {};
  add(`Temperature +${state.horizon}h`, el("div", {}, [el("div", { className: "stat-value" }, [`${f1(temp.prediction)}°C`]), el("div", { className: "stat-sub" }, [`P10 ${f1(temp.p10)} / P90 ${f1(temp.p90)}`]), el("div", { className: "stat-sub" }, [temp.model || ""])]));
  const feel = t.apparent_temperature || {};
  add("Feels Like", el("div", { className: "stat-value" }, [`${f1(feel.prediction)}°C`]));
  const hum = t.humidity || {};
  add("Humidity", el("div", { className: "stat-value" }, [`${f0(hum.prediction)}%`]));
  const rain = t.rain_occurrence || {};
  const amt = t.precipitation_amount || {};
  add("Rain", el("div", {}, [el("div", { className: "stat-value" }, [`${f0((rain.rain_probability ?? 0) * 100)}%`]), el("div", { className: "stat-sub" }, [`${f1(amt.prediction)} mm - ${full.rain_intensity || "-"}`])]));
  const wind = t.wind_speed || {};
  const gust = t.wind_gusts || {};
  const dir = t.wind_direction || {};
  add("Wind", el("div", {}, [el("div", { className: "stat-value" }, [`${f1(wind.prediction)} km/h`]), el("div", { className: "stat-sub" }, [`Gust ${f1(gust.prediction)} - ${dir.direction || "-"}`])]));
  const pres = t.pressure || {};
  add("Pressure", el("div", { className: "stat-value" }, [`${f0(pres.prediction)} hPa`]));
  const dew = t.dew_point || {};
  add("Dew Point", el("div", { className: "stat-value" }, [`${f1(dew.prediction)}°C`]));
  const cloud = t.cloud_cover || {};
  add("Cloud Cover", el("div", { className: "stat-value" }, [`${f0(cloud.prediction)}%`]));
  const vis = t.visibility || {};
  add("Visibility", el("div", { className: "stat-value" }, [`${f1(vis.prediction)} m`]));
  const cond = t.weather_condition || {};
  add("Condition", el("div", { className: "stat-value" }, [cond.condition || "-"]));
  c.appendChild(g);
  const risk = full.risk || {};
  c.appendChild(el("div", { style: "margin-top:16px" }, [card("Risk Signals", el("div", {}, [
    el("div", { className: "risk-row" }, [el("span", {}, ["Heat"]), badge((risk.heat || {}).level || "-", "warning")]),
    el("div", { className: "risk-row" }, [el("span", {}, ["Heavy rain"]), badge((risk.heavy_rain || {}).level || "-", "danger")]),
    el("div", { className: "risk-row" }, [el("span", {}, ["High wind"]), badge((risk.high_wind || {}).level || "-", "info")]),
  ]))]));
}

async function renderModels(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Models"]));
  const models = await api("/api/v1/models");
  c.appendChild(card("Registry", table(["ID", "Name", "Task", "Horizon", "Stage"], models.map((m) => [m.id.slice(0, 12), m.model_name, m.task, m.horizon_hours + "h", badge(m.stage, m.stage === "Champion" ? "success" : m.stage === "Challenger" ? "warning" : "muted")]))));
}

async function renderAccuracy(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Forecast Accuracy"]));
  const ver = await api("/api/v1/verification");
  if (!ver.length) return c.appendChild(card("No verification yet", el("div", { className: "muted" }, ["Run predictions, then 'atmosiq monitor' to verify against actuals."])));
  c.appendChild(card("Verified vs Actuals", table(["Task", "Horizon", "N", "MAE", "RMSE", "Bias"], ver.map((v) => [v.task, v.horizon_hours + "h", v.n, f1(v.mae), f1(v.rmse), f1(v.bias)]))));
}

async function renderDrift(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Drift Monitoring"]));
  const events = await api("/api/v1/monitoring/drift");
  c.appendChild(card("Drift Events", table(["Feature", "PSI", "KS", "p-value", "Threshold", "Detected", "Time"], events.map((e) => [e.feature, e.psi, e.ks_statistic, e.p_value, e.threshold, badge(e.detected ? "yes" : "no", e.detected ? "danger" : "success"), e.timestamp]))));
}

async function renderAlerts(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["Alerts"]));
  const alerts = await api("/api/v1/alerts");
  c.appendChild(card("Alerts", table(["Severity", "Type", "Scope", "Message", "Status", "Created"], alerts.map((a) => [badge(a.severity, a.severity === "CRITICAL" ? "danger" : a.severity === "WARNING" ? "warning" : "info"), a.alert_type, a.scope, a.message, a.status, a.created_at]))));
}

async function renderHealth(c) {
  c.appendChild(el("h2", { className: "page-title" }, ["System Health"]));
  const live = await api("/health/live");
  const ready = await api("/health/ready").catch(() => ({ status: "down" }));
  const summary = await api("/api/v1/monitoring/summary").catch(() => null);
  const g = el("div", { className: "grid cols-4" });
  g.appendChild(card("Live", el("div", { className: "stat-value" }, [live.status])));
  g.appendChild(card("Ready", el("div", { className: "stat-value" }, [ready.status])));
  if (summary) {
    g.appendChild(card("Champions", el("div", { className: "stat-value" }, [String(summary.champion_count)])));
    g.appendChild(card("Open Alerts", el("div", { className: "stat-value" }, [String(summary.active_alerts)])));
  }
  c.appendChild(g);
}

function buildSidebar() {
  const nav = document.getElementById("sidebar");
  nav.innerHTML = "";
  for (const p of PAGES) {
    if (p.group) nav.appendChild(el("div", { className: "group" }, [p.group]));
    nav.appendChild(el("a", { href: `#${p.route}`, "data-route": p.route }, [p.title]));
  }
}
function highlight() {
  const path = location.hash.replace(/^#/, "") || "overview";
  document.querySelectorAll("#sidebar a").forEach((a) => a.classList.toggle("active", a.getAttribute("data-route") === path));
}
async function initTopbar() {
  const locSel = document.getElementById("locSelect");
  const horSel = document.getElementById("horizonSelect");
  const locations = await api("/api/v1/locations").catch(() => []);
  locSel.innerHTML = "";
  locations.forEach((l) => locSel.appendChild(el("option", { value: l.id }, [l.name])));
  if (locations.length) state.location = locations[0].id;
  locSel.onchange = () => { state.location = locSel.value; router(); };
  horSel.innerHTML = "";
  [1, 3, 6, 12, 24, 48, 72].forEach((h) => horSel.appendChild(el("option", { value: h }, ["+" + h + "h"])));
  horSel.value = "24";
  horSel.onchange = () => { state.horizon = Number(horSel.value); router(); };
  document.getElementById("refreshBtn").onclick = () => router();
  document.getElementById("updatedLabel").textContent = "Updated " + new Date().toLocaleTimeString();
}
async function router() {
  const path = location.hash.replace(/^#/, "") || "overview";
  const page = PAGES.find((p) => p.route === path) || PAGES[0];
  const content = document.getElementById("content");
  content.innerHTML = "";
  highlight();
  try {
    await page.render(content);
  } catch (e) {
    content.appendChild(card("Error", el("div", { className: "muted" }, [String(e)])));
  }
}
buildSidebar();
initTopbar();
window.addEventListener("hashchange", router);
router();
'''

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 6 written: {len(W)} files.")
