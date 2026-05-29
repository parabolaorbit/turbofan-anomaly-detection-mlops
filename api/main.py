from __future__ import annotations

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from src.prediction_logger import save_prediction_log
from sqlalchemy.orm import Session

from src.inference import DEFAULT_MODEL_PATH, DEFAULT_SCALER_PATH, load_artifacts
from src.sqlite_logger import save_prediction_log_to_sqlite
from db.database import SessionLocal, engine
from db.models import Base
from db.crud import create_prediction_log
from repositories.prediction_log_repository import PredictionLogRepository
import yaml
from services.prediction_service import PredictionService


CONFIG_PATH = Path("config/config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)
MODEL_VERSION = CONFIG["model"]["version"]
PREDICTION_LOG_PATH = Path(CONFIG["logging"]["prediction_log_path"])
SQLITE_PATH = Path(CONFIG["logging"]["sqlite_path"])

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Turbofan Anomaly API")
router = APIRouter()
# Base.metadata.create_all(bind=engine)

model = None
scaler = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    PredictionService.feature_cols = feature_cols
    logger.info("Loaded model artifacts.")


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None and scaler is not None,
    }

@router.post("/predict_batch")
def predict_batch(
    request: PredictRequest,
    db: Session = Depends(get_db)
):
    pass

@router.post("/predict")
async def predict(
    request: PredictRequest,
    db: Session = Depends(get_db)
):
    if model is None or scaler is None or feature_cols is None:
        raise HTTPException(
            status_code=503,
            detail="Model artifacts are not loaded. Run `python -m src.train` and rebuild the image.",
        )
    
    try:
        logger.info("Received prediction request")
        repository = PredictionLogRepository(db)

        service = PredictionService(
            repository=repository,
            model=model,
            scaler=scaler,
            threshold=request.threshold,
        )

        response = service.predict(dump_request(request))
        return response
    except HTTPException:
        raise
    except KeyError as e:
        logger.warning("Bad request: missing column %s", e)
        raise HTTPException(status_code=400, detail=f"Missing required column: {e}") from e
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


app.include_router(router)
