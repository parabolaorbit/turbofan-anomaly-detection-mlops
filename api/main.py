from __future__ import annotations

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.inference import DEFAULT_MODEL_PATH, DEFAULT_SCALER_PATH, load_artifacts
from db.database import SessionLocal
from repositories.prediction_log_repository import PredictionLogRepository
from services.prediction_service import PredictionService
from api.api_model import PredictRequest
from contextlib import asynccontextmanager

# 実行ログ定義
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

model = None
scaler = None
feature_cols = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, scaler, feature_cols
    if not Path(DEFAULT_MODEL_PATH).exists() or not Path(DEFAULT_SCALER_PATH).exists():
        logger.warning("Model artifacts were not found. Run `python -m src.train` first.")
        yield

    model, scaler, feature_cols = load_artifacts()
    logger.info("Loaded model artifacts.")
    yield

# FastAPI 
app = FastAPI(title="Turbofan Anomaly API", lifespan=lifespan)
# FastAPI Router導入
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def dump_request(request: BaseModel) -> dict:
    if hasattr(request, "model_dump"):
        return request.model_dump()
    return request.dict()

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
    if model is None or scaler is None or feature_cols is None:
        raise HTTPException(
            status_code=503,
            detail="Model artifacts are not loaded. Run `python -m src.train` and rebuild the image.",
        )
    try:
        logger.info("Received prediction request")
        repository = PredictionLogRepository(db)

        # ビジネスロジックはServiceに移譲。Serviceのインスタンス化。
        service = PredictionService(
            repository=repository,
            model=model,
            scaler=scaler,
            threshold=request.threshold,
            feature_cols=feature_cols
        )
        # バッチ版予測を実行
        response = service.predict_batch(dump_request(request))
        # 結果を返却
        return response
    except HTTPException:
        raise
    except KeyError as e:
        logger.warning("Bad request: missing column %s", e)
        raise HTTPException(status_code=400, detail=f"Missing required column: {e}") from e
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

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

        # ビジネスロジックはServiceに移譲。Serviceのインスタンス化。
        service = PredictionService(
            repository=repository,
            model=model,
            scaler=scaler,
            threshold=request.threshold,
            feature_cols=feature_cols
        )
        # 予測を実行
        response = service.predict(dump_request(request))
        # 結果を返却
        return response
    except HTTPException:
        raise
    except KeyError as e:
        logger.warning("Bad request: missing column %s", e)
        raise HTTPException(status_code=400, detail=f"Missing required column: {e}") from e
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

# FastAPI ルーティング xxxに記述する必要あり
app.include_router(router)
