# bootstrap4.py  ->  run: python bootstrap4.py   (inside AtmosIQ_/)
import os

W = {}

W["README.md"] = r'''
# AtmosIQ

Production-oriented weather ML platform built on the NetworkSecurity architecture
(ConfigEntity -> Component -> Artifact -> Pipeline), extended with multi-horizon weather
forecasting, rain prediction, strong baselines, classical ML, Optuna, LSTM/GRU/TCN/Transformer,
probabilistic forecasting, MLflow, a model registry with quality gates, PostgreSQL, FastAPI,
Prometheus, OpenTelemetry, drift/performance monitoring, alerting, retraining, Docker, and CI/CD.

This is production-oriented, not production-proven. Treat it as a serious engineering foundation.

## Quickstart (local, no Docker)

    pip install -e ".[dev]"
    atmosiq db-migrate
    pytest -q
    uvicorn atmosiq.api.app:app --reload

Then open http://localhost:8000/docs and http://localhost:8000/static/index.html

## Pipeline (real weather data via Open-Meteo)

    atmosiq ingest
    atmosiq train
    atmosiq monitor
    atmosiq retrain --reason manual
    atmosiq predict --task temperature --horizon 24

## Configuration

- config/atmosiq.yaml : locations, horizons, validation ranges, quality gate policy, drift thresholds
- data_schema/weather_schema.yaml : canonical hourly schema
- DATABASE_URL : default sqlite:///atmosiq.db for local dev; set PostgreSQL URL for production
- MLFLOW_TRACKING_URI : experiment tracking + model registry

## Production stack (Docker)

    cd docker
    docker compose up --build

Services: postgres, redis, mlflow, api, worker, prometheus, grafana, jaeger.

See docs/architecture_map.md for the NetworkSecurity -> AtmosIQ mapping.
'''

W["docs/architecture_map.md"] = r'''
# Architecture map: NetworkSecurity -> AtmosIQ

| NetworkSecurity | AtmosIQ equivalent | Reason |
|---|---|---|
| constant/training_pipeline/__init__.py | same path | same constant philosophy, extended |
| entity/config_entity.py | same path | same TrainingPipelineConfig + per-component configs |
| entity/artifact_entity.py | same path | same dataclass artifacts |
| exception/exception.py | same path | identical pattern, renamed AtmosIQException |
| logging/logger.py | same path | same module-import pattern, upgraded to JSON |
| utils/main_utils | same path | same helpers + parquet/json/hash/seed |
| utils/ml_utils/{metric,model} | same paths | metrics + ModelFactory |
| components/* | same pattern | Mongo source swapped for providers/ layer |
| pipeline/training_pipeline.py | same path | same orchestration |
| data_schema/schema.yaml | data_schema/weather_schema.yaml | same schema-file idea |
| app.py | api/app.py | FastAPI kept, productionized |

New AtmosIQ layers (extensions): providers/, db/, utils/leakage_guard.py,
feature_engineering, dataset_creation, baseline_trainer, hyperparameter_tuner,
deep (LSTM/GRU/TCN/Transformer), quantile_models, model_evaluation, model_pusher,
prediction_service, drift_monitor, performance_monitor, alert_manager,
retraining_service, observability/, api/, worker.py.
'''

W["push.sh"] = r'''
#!/usr/bin/env bash
# Usage: ./push.sh https://github.com/<user>/<repo>.git
set -e
REPO="${1:?usage: ./push.sh <git-remote-url>}"
git init
git add .
git commit -m "AtmosIQ: initial import"
git branch -M main
git remote add origin "$REPO"
git push -u origin main
'''

for path, content in W.items():
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))

print(f"Part 4 written: {len(W)} files.")