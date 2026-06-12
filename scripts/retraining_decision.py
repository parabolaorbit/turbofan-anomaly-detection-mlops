import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from core.config import settings


def fetch_recent_metrics(limit: int = 100) -> dict:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    prediction AS anomaly_score,
                    alert,
                    final_alert,
                    severity,
                    sensor_ms2_mean
                FROM prediction_logs
                ORDER BY id DESC
                LIMIT :limit
            """),
            {"limit": limit},
        ).mappings().all()

    if not rows:
        return {
            "count": 0,
            "avg_score": None,
            "alert_rate": None,
            "final_alert_rate": None,
            "sensor_ms2_mean": None,
        }

    count = len(rows)
    avg_score = sum(row["anomaly_score"] for row in rows) / count
    alert_rate = sum(bool(row["alert"]) for row in rows) / count
    final_alert_rate = sum(bool(row["final_alert"]) for row in rows) / count

    sensor_values = [
        row["sensor_ms2_mean"]
        for row in rows
        if row["sensor_ms2_mean"] is not None
    ]
    sensor_ms2_mean = (
        sum(sensor_values) / len(sensor_values)
        if sensor_values
        else None
    )

    return {
        "count": count,
        "avg_score": avg_score,
        "alert_rate": alert_rate,
        "final_alert_rate": final_alert_rate,
        "sensor_ms2_mean": sensor_ms2_mean,
    }


def decide_retraining(metrics: dict) -> str:
    if metrics["count"] < 30:
        return "WATCH: not enough data"

    if metrics["final_alert_rate"] >= 0.1:
        return "REVIEW: final_alert_rate is high"

    if metrics["alert_rate"] >= 0.2:
        return "REVIEW: alert_rate is high"

    if metrics["avg_score"] >= 0.6:
        return "WATCH: avg anomaly_score is rising"

    if metrics["sensor_ms2_mean"] is not None:
        baseline_sensor_ms2 = 642.2
        drift_ratio = abs(metrics["sensor_ms2_mean"] - baseline_sensor_ms2) / baseline_sensor_ms2

        if drift_ratio >= 0.1:
            return "REVIEW: sensor_ms2 drift detected"

    return "NO_ACTION"


if __name__ == "__main__":
    metrics = fetch_recent_metrics(limit=100)
    decision = decide_retraining(metrics)

    print("metrics:", metrics)
    print("decision:", decision)