# AtmosIQ — AI Weather Intelligence & ML Forecasting Platform

[![CI](https://github.com/atmosiq/atmosiq/actions/workflows/ci.yml/badge.svg)](https://github.com/atmosiq/atmosiq/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)

## Overview

AtmosIQ is a production-grade weather intelligence platform that combines:

- **Real-time weather observations** from Open-Meteo (ERA5 datasets)
- **ML-powered forecasts** using LightGBM, XGBoost, CatBoost, and LSTM models
- **Probabilistic predictions** with uncertainty bounds (p10-p90 percentiles)
- **Automated MLOps** including drift detection, data quality monitoring, and model registry
- **Professional dashboard** built with Next.js 16 + React 19

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│  FastAPI     │────▶│ PostgreSQL  │
│  Next.js 16 │◀────│  Backend     │◀────│  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  ML Models   │
                   │  (trained)   │
                   └──────────────┘
```

## Features

### Weather Intelligence
- Current weather conditions
- Hourly and daily forecasts
- Historical weather analysis
- Geospatial weather maps

### AI Forecasting
- Temperature prediction with uncertainty intervals
- Rainfall forecasting (probability + amount)
- Wind speed and direction prediction
- Multi-model comparison

### ML Operations
- Model performance tracking (MAE, RMSE, skill scores)
- Forecast verification against actuals
- Feature drift detection (PSI, KS tests)
- Data quality monitoring
- Training run audit trail

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 15+

### Backend Setup

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn src.atmosiq.api.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Generate ML Predictions

```bash
# Run the bootstrap pipeline to generate predictions
python bootstrap1.py
```

## Project Structure

```
atmosiq/
├── src/atmosiq/          # Main Python package
│   ├── api/              # FastAPI endpoints
│   ├── config/           # Configuration management
│   ├── data/             # Data ingestion & validation
│   ├── features/         # Feature engineering
│   ├── ml/               # ML training & inference
│   ├── models/           # SQLAlchemy ORM models
│   ├── monitoring/       # Drift & quality monitoring
│   └── utils/            # Utilities
├── frontend/             # Next.js application
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/              # API clients & utilities
│   └── services/         # Data services
├── tests/                # Test suite
└── alembic/              # Database migrations
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/weather/current` | Current weather conditions |
| `/api/v1/weather/hourly` | Hourly forecast |
| `/api/v1/weather/daily` | Daily forecast |
| `/api/v1/forecast/temperature` | ML temperature predictions |
| `/api/v1/forecast/rainfall` | Rainfall forecasts |
| `/api/v1/forecast/wind` | Wind predictions |
| `/api/v1/ml/performance` | Model metrics |
| `/api/v1/ml/verification` | Forecast verification |
| `/api/v1/mlops/drift` | Drift monitoring |
| `/api/v1/mlops/data-quality` | Data quality checks |
| `/api/v1/system/health` | System health status |

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src/atmosiq

# Frontend tests
cd frontend && npm test
```

## Production Deployment

1. Set environment variables for database, API keys
2. Run database migrations: `alembic upgrade head`
3. Build frontend: `cd frontend && npm run build`
4. Start backend with production server
5. Serve frontend static files via nginx or similar

## License

MIT License
