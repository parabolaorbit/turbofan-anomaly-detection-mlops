from repositories.prediction_log_repository import PredictionLogRepository
from src.inference import predict_anomaly_one
from fastapi import FastAPI, HTTPException
import time
import pandas as pd
from src.dataset import FEATURE_COLUMNS, add_cycle_norm

MODEL_VERSION = "v1"
feature_cols = None

class PredictionService:
    def __init__(
            self,
            repository: PredictionLogRepository,
            model,
            scaler,
            threshold: float,
    ):
        self.repository = repository
        self.model = model
        self.scaler = scaler
        self.threshold = threshold

    def predict(self, input_data):
        start_time = time.perf_counter()
        seq_len = input_data.get("seq_len", 10)
        data = pd.DataFrame(input_data["sequence"])
        # 前処理
        feature_cols = self.feature_cols or FEATURE_COLUMNS
        if "cycle_norm" not in data.columns:
            data = add_cycle_norm(data)

        data = data.sort_values(["unit_number", "time_in_cycles"]).reset_index(drop=True)
        data[feature_cols] = self.scaler.transform(data[feature_cols])
        # 推論
        result = predict_anomaly_one(
            sequence=data, 
            model=self.model,
            feature_cols=feature_cols,
            )

        
        latency_ms = (time.perf_counter() - start_time) * 1000

        if result.empty:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"sequence must contain at least seq_len={seq_len} records "
                    "for the same unit_number"
                ),
            )
    
        latest = result.sort_values(["unit_number", "time_in_cycles"]).iloc[-1]
        severity = "normal"
        if bool(latest["final_alert"]):
            severity = "critical"
        elif bool(latest["alert"]):
            severity = "warning"

        sensor_errors = latest[[c for c in result.columns if c.startswith("sensor_error_")]]
        top_sensor_errors = [
            {
                "sensor": sensor_name.replace("sensor_error_", ""),
                "error": float(error_value),
            }
            for sensor_name, error_value in sensor_errors.sort_values(ascending=False).head(5).items()
        ]

        sensor_ms2_mean = data["sensor_ms2"].mean()
        sensor_ms3_mean = data["sensor_ms3"].mean()
        sensor_ms4_mean = data["sensor_ms4"].mean()

        response = {
            "unit_number": int(latest["unit_number"]),
            "time_in_cycles": int(latest["time_in_cycles"]),
            "error": float(latest["error"]),
            "rolling_error": float(latest["rolling_error"]),
            "threshold": float(self.threshold),
            "alert": bool(latest["alert"]),
            "final_alert": bool(latest["final_alert"]),
            "severity": severity,
            "top_sensor_errors": top_sensor_errors,
            "model_version": MODEL_VERSION,
            "latency_ms": latency_ms,
            "sensor_ms2_mean": float(sensor_ms2_mean),
            "sensor_ms3_mean": float(sensor_ms3_mean),
            "sensor_ms4_mean": float(sensor_ms4_mean),
        }
        # 判定
        final_result = "anomaly" if bool(latest["final_alert"]) else "normal"
        # ログ保存
        self.repository.create(
            prediction=float(latest["rolling_error"]),
            threshold=float(self.threshold),
            result=final_result,
        )
        # レスポンス
        return {
            "prediction": float(latest["rolling_error"]),
            "threshold": float(self.threshold),
            "result": final_result,
        }
