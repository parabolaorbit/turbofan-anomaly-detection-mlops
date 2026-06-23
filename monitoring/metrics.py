from prometheus_client import Counter, Histogram, Gauge

prediction_requests_total = Counter(
    "prediction_requests_total",
    "Total prediction requests"
)

anomaly_predictions_total = Counter(
    "anomaly_predictions_total",
    "Total anomaly predictions"
)

prediction_latency_seconds = Histogram(
    "prediction_latency_seconds",
    "Prediction latency"
)

reconstruction_error_gauge = Gauge(
    "reconstruction_error",
    "Current reconstruction error"
)

rolling_error_gauge = Gauge(
    "rolling_error",
    "Current rolling anomaly score"
)

sensor_ms2_mean_gauge = Gauge(
    "sensor_ms2_mean",
    "Mean value of sensor ms2"
)
"""
model_version_counter = Counter(

)

#severity_counter
severity_normal_total = Counter(

)
severity_warning_total = Counter(

)
severity_critical_total = Counter(

)

drift_score_gauge
"""