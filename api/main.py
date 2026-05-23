from __future__ import annotations

import logging
from pathlib import Path

import time
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.prediction_logger import save_prediction_log

from src.inference import DEFAULT_MODEL_PATH, DEFAULT_SCALER_PATH, load_artifacts, predict_anomaly
from src.sqlite_logger import save_prediction_log_to_sqlite
import yaml

MODEL_VERSION = "v1"
CONFIG_PATH = Path("config/config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)
MODEL_VERSION = CONFIG["model"]["version"]
PREDICTION_LOG_PATH = Path(CONFIG["logging"]["prediction_log_path"])
SQLITE_PATH = Path(CONFIG["logging"]["sqlite_path"])

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Turbofan Anomaly API")

model = None
scaler = None
feature_cols = None

class SensorRecord(BaseModel):
    unit_number: int
    time_in_cycles: int
    ope_setting1: float
    ope_setting2: float
    ope_setting3: float
    sensor_ms1: float
    sensor_ms2: float
    sensor_ms3: float
    sensor_ms4: float
    sensor_ms5: float
    sensor_ms6: float
    sensor_ms7: float
    sensor_ms8: float
    sensor_ms9: float
    sensor_ms10: float
    sensor_ms11: float
    sensor_ms12: float
    sensor_ms13: float
    sensor_ms14: float
    sensor_ms15: float
    sensor_ms16: float
    sensor_ms17: float
    sensor_ms18: float
    sensor_ms19: float
    sensor_ms20: float
    sensor_ms21: float


class PredictRequest(BaseModel):
    sequence: list[SensorRecord] = Field(..., min_length=1)
    seq_len: int = 10
    rolling_window: int = 10
    threshold: float = 0.8
    consecutive_window: int = 5


def dump_request(request: BaseModel) -> dict:
    if hasattr(request, "model_dump"):
        return request.model_dump()
    return request.dict()


@app.on_event("startup")
def startup() -> None:
    global model, scaler, feature_cols
    if not Path(DEFAULT_MODEL_PATH).exists() or not Path(DEFAULT_SCALER_PATH).exists():
        logger.warning("Model artifacts were not found. Run `python -m src.train` first.")
        return

    model, scaler, feature_cols = load_artifacts()
    logger.info("Loaded model artifacts.")


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None and scaler is not None,
    }


@app.post("/predict")
def predict(request: PredictRequest):
    if model is None or scaler is None or feature_cols is None:
        raise HTTPException(
            status_code=503,
            detail="Model artifacts are not loaded. Run `python -m src.train` and rebuild the image.",
        )
    start_time = time.perf_counter()
    try:
        logger.info("Received prediction request")
        request_data = dump_request(request)
        sequence_df = pd.DataFrame(request_data["sequence"])

        result = predict_anomaly(
            sequence_df,
            model=model,
            scaler=scaler,
            feature_cols=feature_cols,
            seq_len=request.seq_len,
            rolling_window=request.rolling_window,
            threshold=request.threshold,
            consecutive_window=request.consecutive_window,
        )
        if result.empty:
            raise HTTPException(
                status_code=400,
                detail="No prediction rows were created. Check sequence length and input rows.",
            )
        latency_ms = (time.perf_counter() - start_time) * 1000

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

        sensor_ms2_mean = sequence_df["sensor_ms2"].mean()
        sensor_ms3_mean = sequence_df["sensor_ms3"].mean()
        sensor_ms4_mean = sequence_df["sensor_ms4"].mean()

        response = {
            "unit_number": int(latest["unit_number"]),
            "time_in_cycles": int(latest["time_in_cycles"]),
            "error": float(latest["error"]),
            "rolling_error": float(latest["rolling_error"]),
            "threshold": request.threshold,
            "alert": bool(latest["alert"]),
            "final_alert": bool(latest["final_alert"]),
            "severity": severity,
            "top_sensor_errors": top_sensor_errors,
            "model_version": MODEL_VERSION,
            "latency_ms": latency_ms,
            "sensor_ms2_mean": sensor_ms2_mean,
            "sensor_ms3_mean": sensor_ms3_mean,
            "sensor_ms4_mean": sensor_ms4_mean,
        }

        save_prediction_log(
            log_path=PREDICTION_LOG_PATH,
            input_data=dump_request(request),
            prediction_result=response,
            model_version=MODEL_VERSION,
        )

        save_prediction_log_to_sqlite(
            db_path=SQLITE_PATH,
            input_data=dump_request(request),
            prediction_result=response,
            model_version=MODEL_VERSION,
        )

        return response
    except HTTPException:
        raise
    except KeyError as e:
        logger.warning("Bad request: missing column %s", e)
        raise HTTPException(status_code=400, detail=f"Missing required column: {e}") from e
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
