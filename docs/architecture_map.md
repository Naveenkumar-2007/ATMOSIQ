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
