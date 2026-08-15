# 🌤️ AtmosIQ — AI-Powered Weather Intelligence & MLOps Platform

<div align="center">

![Next.js 16](https://img.shields.io/badge/Frontend-Next.js%2016%20%2F%20React%2019-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2F%20Python-009688?logo=fastapi&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-LightGBM%20%7C%20XGBoost%20%7C%20CatBoost%20%7C%20LSTM-blue)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2F%20SQLAlchemy-336791?logo=postgresql&logoColor=white)
![MLOps](https://img.shields.io/badge/MLOps-Optuna%20%7C%20Prometheus%20%7C%20Drift-orange)

**Enterprise-grade AI weather intelligence platform delivering multi-horizon predictive forecasting, probabilistic uncertainty bounds, automated drift detection, and full-stack MLOps observability.**

[Explore Live Dashboard](#quickstart) • [API Documentation](#api-reference) • [Architecture](#system-architecture) • [ML Pipelines](#machine-learning-capabilities)

</div>

---

## 🚀 Overview

AtmosIQ pairs an automated Python ML pipeline with a high-performance Next.js 16 SaaS frontend. Built on meteorological reanalysis datasets (Open-Meteo ERA5), the platform trains champion and challenger models across multiple atmospheric targets, evaluates them against physical baseline models, and delivers live inference with quantified uncertainty bounds ($p_{10}$ to $p_{90}$).

### Key Highlights
- **21 Dedicated SaaS Pages**: Comprehensive views spanning Executive KPIs, Weather Intelligence, AI Predictive Forecasting, Model Registries, Data Quality Gates, Feature Drift Monitoring, and System Telemetry.
- **Probabilistic Forecasting**: Quantile gradient boosting ($p_{10}$, $p_{50}$, $p_{90}$) providing reliable uncertainty intervals for risk-critical operations.
- **Dual-Model Precipitation**: Combining CatBoost classification for rain occurrence and LightGBM regression for quantitative precipitation volume.
- **Automated MLOps Quality Gates**: Automated drift monitoring (Population Stability Index & Kolmogorov-Smirnov test), dataset validation, and model promotion pipelines.

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          AtmosIQ Frontend                              │
│            (Next.js 16 • React 19 • Recharts • CSS Design System)      │
│       21 Pages: Dashboard, Weather, Forecast, ML Intel, MLOps, System  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST API (/api/v1/*)
┌───────────────────────────────────▼────────────────────────────────────┐
│                           FastAPI Service Layer                        │
│   (Predict API, Historical/Forecast Data, Monitoring, Model Registry)  │
└──────────────────┬─────────────────┬───────────────────┬───────────────┘
                   │                 │                   │
┌──────────────────▼──────┐ ┌────────▼─────────┐ ┌───────▼───────────────┐
│     PostgreSQL DB       │ │ Model Artifacts  │ │ Open-Meteo ERA5 /     │
│ (Observations, Forecasts│ │ & Registry       │ │ Multi-provider Data   │
│ Predictions, Drift Logs)│ │ (Champions/Chall)│ │ Ingestion Pipelines   │
└─────────────────────────┘ └──────────────────┘ └───────────────────────┘
```

---

## 💻 Quickstart

### 1. Backend Setup & Database
```bash
# Clone the repository
git clone https://github.com/Naveenkumar-2007/ATMOSIQ.git
cd ATMOSIQ

# Setup Virtual Environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run database schema migrations
python -m atmosiq.cli db-migrate
```

### 2. Ingest Data & Train ML Models
```bash
# Ingest meteorological observations
python -m atmosiq.cli ingest

# (Optional) Multi-city historical ingestion for Indian regions
python src/atmosiq/ingest_india.py

# Run automated Data Quality Checks
python -m atmosiq.cli validate

# Train Champion and Challenger ML Models
python -m atmosiq.cli train

# Execute verification and drift analysis
python -m atmosiq.cli monitor
```

### 3. Launch FastAPI Server
```bash
python -m uvicorn atmosiq.api.app:app --host 127.0.0.1 --port 8000 --reload
```
- **Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Telemetry**: [http://127.0.0.1:8000/api/v1/system/health](http://127.0.0.1:8000/api/v1/system/health)

### 4. Launch Next.js SaaS Dashboard
```bash
cd frontend
npm install
npm run dev
```
- **Platform URL**: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)

---

## 📊 Platform Navigation & Pages

```
├── Executive Dashboard:
│   └── /dashboard                 (Overview KPI, 24h & 7d Weather, ML Status, Health)
├── Weather Intelligence:
│   ├── /weather/current           (Live Observed Conditions & 10 Metric Tiles)
│   ├── /weather/hourly            (24h/48h Multi-parameter Hourly Forecast & Recharts)
│   ├── /weather/daily             (7-Day Outlook Cards, Temp Range, Precipitation)
│   ├── /weather/history           (3/7/14/30-Day Timeseries & Analytics Table)
│   └── /weather/map               (Interactive Station Map & Spatial Coordinates)
├── AI Predictive Forecast:
│   ├── /forecast/temperature      (Champion Model Telemetry, p10-p90 Uncertainty Bounds)
│   ├── /forecast/rainfall         (Dual-Model Rain Occurrence & Precipitation Amount)
│   ├── /forecast/wind             (Speed, Gusts & Direction Predictions)
│   └── /forecast/comparison       (Ground Truth vs ML Forecast vs NWP Baseline)
├── ML Intelligence & Registry:
│   ├── /ml/performance            (Model Performance Leaderboard & Cross-Task MAE)
│   ├── /ml/verification           (Forecast vs Actual Scatter Plot & Residuals)
│   ├── /ml/predictions            (Paginated Prediction Audit Trail)
│   └── /ml/models                 (Model Registry with Stage Lifecycle Transitions)
├── MLOps & Observability:
│   ├── /mlops/data-quality        (Automated Schema & Quality Gate Validation)
│   ├── /mlops/drift               (Population Stability Index & Distribution Shift)
│   ├── /mlops/model-monitoring    (24h/7d Volume, Latency, Error Rates)
│   ├── /mlops/training-runs       (Hyperparameter & Experiment Run Tracking)
│   └── /mlops/alerts              (Anomaly Alerts with Acknowledge & Resolve)
└── Platform System:
    ├── /system/health             (PostgreSQL, FastAPI, ML Models status)
    └── /settings                  (Theme Switcher, Station Selectors)
```

---

## 🛠️ Tech Stack

- **ML Frameworks**: LightGBM, XGBoost, CatBoost, Scikit-learn, Optuna
- **Backend API**: FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic v2
- **Data Engineering**: Pandas, NumPy, Great Expectations
- **Observability**: Prometheus, Grafana, OpenTelemetry, Loguru
- **Frontend App**: Next.js 16 (App Router), React 19, Recharts, Lucide Icons, Vanilla CSS Design System

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
