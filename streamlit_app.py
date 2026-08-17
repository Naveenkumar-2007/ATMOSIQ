import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


def secret_or_env(name, default=""):
    env_value = os.getenv(name)
    if env_value:
        return env_value
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


API_BASE = secret_or_env("ATMOSIQ_API_URL", "https://atmosiq-rjd5.onrender.com").rstrip("/")
TRIGGER_TOKEN = secret_or_env("MLOPS_TRIGGER_TOKEN", "")


st.set_page_config(
    page_title="AtmosIQ MLOps Weather Intelligence",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
      .block-container { padding-top: 1.25rem; }
      [data-testid="stSidebar"] { background: #0b132b; }
      [data-testid="stSidebar"] * { color: #e2e8f0; }
      .metric-card {
        border: 1px solid rgba(148,163,184,.22);
        border-radius: 14px;
        padding: 16px;
        background: linear-gradient(180deg, rgba(15,23,42,.98), rgba(15,23,42,.92));
      }
      .small-muted { color: #94a3b8; font-size: 0.82rem; }
      .status-good { color: #34d399; font-weight: 700; }
      .status-warn { color: #fbbf24; font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path, default=None, params=None):
    try:
        res = requests.get(f"{API_BASE}{path}", params=params, timeout=45)
        res.raise_for_status()
        return res.json()
    except Exception as exc:
        st.warning(f"API unavailable for {path}: {exc}")
        return default


def api_post(path):
    headers = {"x-atmosiq-token": TRIGGER_TOKEN} if TRIGGER_TOKEN else {}
    res = requests.post(f"{API_BASE}{path}", headers=headers, timeout=90)
    res.raise_for_status()
    return res.json()


def metric_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="small-muted">{label}</div>
          <div style="font-size: 1.75rem; font-weight: 800; margin-top: .25rem;">{value}</div>
          <div class="small-muted">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def normalize_records(data):
    return data if isinstance(data, list) else []


locations = normalize_records(api_get("/api/v1/locations", []))
location_names = {loc["name"]: loc["id"] for loc in locations if "name" in loc and "id" in loc}
if not location_names:
    location_names = {"Kavali": "kavali"}

with st.sidebar:
    st.title("AtmosIQ")
    st.caption("AI Weather Intelligence")
    selected_name = st.selectbox("Station", list(location_names.keys()), index=0)
    location_id = location_names[selected_name]
    page = st.radio(
        "Workspace",
        [
            "Overview",
            "Current Weather",
            "Daily Forecast",
            "Model Registry",
            "Training Runs",
            "MLOps Monitoring",
            "Retraining",
        ],
    )
    st.divider()
    st.caption(f"API: {API_BASE}")


combined = api_get(f"/api/v1/weather/combined/{location_id}", {})
current = combined.get("current", {}) if isinstance(combined, dict) else {}
daily = combined.get("daily", {}) if isinstance(combined, dict) else {}
hourly = combined.get("hourly", {}) if isinstance(combined, dict) else {}


st.title("AtmosIQ Weather MLOps")
st.caption(f"{selected_name} · refreshed {datetime.now().strftime('%d %b %Y, %I:%M %p')}")


if page == "Overview":
    cols = st.columns(6)
    with cols[0]:
        metric_card("Temperature", f"{current.get('temperature_2m', 0):.1f}°C", "Live weather")
    with cols[1]:
        metric_card("Feels Like", f"{current.get('apparent_temperature', 0):.1f}°C")
    with cols[2]:
        metric_card("Humidity", f"{current.get('relative_humidity_2m', 0):.0f}%")
    with cols[3]:
        metric_card("Wind", f"{current.get('wind_speed_10m', 0):.1f} km/h")
    with cols[4]:
        metric_card("Pressure", f"{current.get('pressure_msl', 0):.0f} hPa")
    with cols[5]:
        metric_card("Rain Chance", f"{current.get('summary', {}).get('rain_chance', 0)}%")

    times = hourly.get("times", [])[:24]
    if times:
        chart_df = pd.DataFrame({
            "time": pd.to_datetime(times),
            "temperature": hourly.get("temperature_2m", [])[: len(times)],
            "rain_probability": hourly.get("precipitation_probability", [])[: len(times)],
            "wind_speed": hourly.get("wind_speed_10m", [])[: len(times)],
        }).set_index("time")
        st.subheader("24-hour forecast")
        st.line_chart(chart_df[["temperature", "rain_probability", "wind_speed"]])

elif page == "Current Weather":
    st.subheader("Current Weather Telemetry")
    st.json(current)

elif page == "Daily Forecast":
    dates = daily.get("dates", [])
    if dates:
        df = pd.DataFrame({
            "date": dates,
            "max_temp": daily.get("temperature_max", []),
            "min_temp": daily.get("temperature_min", []),
            "rainfall_mm": daily.get("precipitation_sum", []),
            "rain_probability": daily.get("precipitation_probability_max", []),
            "wind_speed": daily.get("wind_speed_max", []),
        })
        st.dataframe(df, use_container_width=True)
        st.line_chart(df.set_index("date")[["max_temp", "min_temp", "rain_probability"]])
    else:
        st.info("Daily forecast is not available yet.")

elif page == "Model Registry":
    models = normalize_records(api_get("/api/v1/models", []))
    champs = [m for m in models if m.get("stage") == "Champion"]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Models", len(models))
    with c2:
        st.metric("Champions", len(champs))
    with c3:
        st.metric("Tasks", len({m.get("task") for m in models}))
    st.dataframe(pd.DataFrame(models), use_container_width=True)

elif page == "Training Runs":
    runs = normalize_records(api_get("/api/v1/mlops/training-runs", []))
    st.metric("Training Runs", len(runs))
    if runs:
        df = pd.DataFrame(runs)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No training runs recorded yet.")

elif page == "MLOps Monitoring":
    health = api_get("/api/v1/system/health", {})
    monitoring = api_get("/api/v1/mlops/model-monitoring", {})
    perf = api_get("/api/v1/ml/performance", {})
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("System", health.get("status", "unknown"))
    with c2:
        st.metric("Champion Models", monitoring.get("champion_models", 0))
    with c3:
        st.metric("Predictions 24h", monitoring.get("prediction_volume_24h", 0))
    with c4:
        st.metric("Drift Events 30d", monitoring.get("drift_events_30d", 0))
    st.subheader("Performance")
    st.dataframe(pd.DataFrame(perf.get("models", [])), use_container_width=True)

elif page == "Retraining":
    status = api_get("/api/v1/mlops/retraining/status", {})
    st.subheader("Retraining Schedule")
    st.json(status)
    st.caption("Daily retraining is triggered by GitHub Actions or the embedded production worker.")
    if st.button("Trigger retraining now", type="primary"):
        try:
            result = api_post("/api/v1/mlops/retraining/run")
            st.success("Retraining trigger completed.")
            st.json(result)
        except Exception as exc:
            st.error(f"Retraining trigger failed: {exc}")
