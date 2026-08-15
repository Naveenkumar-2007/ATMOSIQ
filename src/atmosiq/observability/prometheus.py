from prometheus_client import Counter, Gauge, Histogram

atmosiq_requests_total = Counter("atmosiq_requests_total", "Total API requests", ["endpoint", "method", "status"])
atmosiq_request_latency_seconds = Histogram("atmosiq_request_latency_seconds", "API request latency", ["endpoint"], buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5))
atmosiq_prediction_total = Counter("atmosiq_prediction_total", "Total model predictions", ["task", "horizon", "model"])
atmosiq_prediction_latency_seconds = Histogram("atmosiq_prediction_latency_seconds", "Prediction latency", ["task", "horizon"])
atmosiq_pipeline_runs_total = Counter("atmosiq_pipeline_runs_total", "Total pipeline runs", ["pipeline", "status"])
atmosiq_training_runs_total = Counter("atmosiq_training_runs_total", "Total training runs", ["model", "task"])
atmosiq_validation_failures_total = Counter("atmosiq_validation_failures_total", "Total validation failures", ["check"])
atmosiq_data_drift_events_total = Counter("atmosiq_data_drift_events_total", "Total drift events", ["feature"])
atmosiq_model_performance = Gauge("atmosiq_model_performance", "Current model performance metric", ["model", "task", "metric"])
atmosiq_model_health = Gauge("atmosiq_model_health", "Model health", ["model", "task"])
atmosiq_alerts_active = Gauge("atmosiq_alerts_active", "Active alerts", ["severity", "alert_type"])
