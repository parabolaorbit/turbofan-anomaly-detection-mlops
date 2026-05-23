import sqlite3
from pathlib import Path
from datetime import datetime, timezone

def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS prediction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model_version TEXT NOT NULL,
                unit_number INTEGER,
                start_cycle INTEGER,
                end_cycle INTEGER,
                sequence_length INTEGER,
                anomaly_score REAL,
                threshold REAL,
                is_anomaly INTEGER,
                latency_ms REAL,
                severity TEXT,
                alert INTEGER,
                final_alert INTEGER,
                sensor_ms2_mean REAL,
                sensor_ms3_mean REAL,
                sensor_ms4_mean REAL
            )
        """)
        conn.commit()

def save_prediction_log_to_sqlite(
        db_path: Path,
        input_data: dict,
        prediction_result: dict,
        model_version: str,
) -> None:
    init_db(db_path)

    sequence = input_data["sequence"]

    unit_number = sequence[0].get("unit_number")
    start_cycle = sequence[0].get("time_in_cycles")
    end_cycle = sequence[-1].get("time_in_cycles")
    sequence_length = len(sequence)

    anomaly_score = prediction_result.get("error")
    threshold = prediction_result.get("threshold")
    is_anomaly = int(prediction_result.get("final_alert", False))
    latency_ms = prediction_result.get("latency_ms")
    severity = prediction_result.get("severity")
    alert = int(prediction_result.get("alert", False))
    final_alert = int(prediction_result.get("final_alert", False))
    sensor_ms2_mean = prediction_result.get("sensor_ms2_mean")
    sensor_ms3_mean = prediction_result.get("sensor_ms3_mean")
    sensor_ms4_mean = prediction_result.get("sensor_ms4_mean")

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
        INSERT INTO prediction_logs (
                     timestamp,
                     model_version,
                     unit_number,
                     start_cycle,
                     end_cycle,
                     sequence_length,
                     anomaly_score,
                     threshold,
                     is_anomaly,
                     latency_ms,
                     severity,
                     alert,
                     final_alert,
                     sensor_ms2_mean,
                     sensor_ms3_mean,
                     sensor_ms4_mean

        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        ,(
            datetime.now(timezone.utc).isoformat(),
            model_version,
            unit_number,
            start_cycle,
            end_cycle,
            sequence_length,
            anomaly_score,
            threshold,
            is_anomaly,
            latency_ms,
            severity,
            alert,
            final_alert,
            sensor_ms2_mean,
            sensor_ms3_mean,
            sensor_ms4_mean
        ))

