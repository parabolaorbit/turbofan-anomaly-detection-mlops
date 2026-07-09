from __future__ import annotations

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, APIRouter, Response, Request, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.inference import DEFAULT_MODEL_PATH, DEFAULT_SCALER_PATH, load_artifacts
from db.database import SessionLocal
from repositories.prediction_log_repository import PredictionLogRepository
from services.prediction_service import PredictionService
from api.api_model import PredictRequest, PredictResponse
from core.security import verify_api_key
from contextlib import asynccontextmanager
from monitoring.metrics import prediction_latency_seconds
from prometheus_client import generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from core.exceptions import rate_limit_handler, internal_server_error_handler
from core.logging_config import setup_logging
from core.const import FASTAPI_PREDICTION_RESPONSE, FASTAPI_PREDICTION_DESCRIPTION

# 実行ログ定義
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
setup_logging()

model = None
scaler = None
feature_cols = None

# FastAPIのライフサイクルイベントでモデルアーティファクトをロード
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, scaler, feature_cols
    if not Path(DEFAULT_MODEL_PATH).exists() or not Path(DEFAULT_SCALER_PATH).exists():
        logger.warning("Model artifacts were not found. Run `python -m src.train` first.")
        yield
        return

    model, scaler, feature_cols = load_artifacts()
    logger.info("Loaded model artifacts.")
    yield

# FastAPI 
app = FastAPI(
    title="Turbofan Anomaly API",
    description=(
        "LSTM AutoEncoder based anomaly detection API"
        " for NASA Turbofan sensor data."
    ),
    version="0.1.0", 
    lifespan=lifespan
)

# Error Handler
app.add_exception_handler(
    RateLimitExceeded,
    rate_limit_handler,
)

app.add_exception_handler(
    Exception,
    internal_server_error_handler,
)

# アクセス制限
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

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

@router.post("/predict_batch",
            tags=["Prediction"],
            summary="Predict anomaly score for Batch",
            description=FASTAPI_PREDICTION_DESCRIPTION,
            response_model=PredictResponse,
            response_description="Prediction result",
            responses=FASTAPI_PREDICTION_RESPONSE,
            dependencies=[Depends(verify_api_key)])
@limiter.limit("5/minute")
def predict_batch(
    request: Request,
    body: PredictRequest,
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
            threshold=body.threshold,
            feature_cols=feature_cols
        )
        # バッチ版予測を実行
        with prediction_latency_seconds.time():
            response = service.predict_batch(dump_request(body))
        # 結果を返却
        return PredictResponse(
                prediction=response["rolling_error"],
                threshold=response["threshold"],
                result=response["result"],
                latency_ms=response["latency_ms"],
                model_version=response["model_version"],
            )
    except HTTPException:
        raise
    except KeyError as e:
        logger.warning("Bad request: missing column %s", e)
        raise HTTPException(status_code=400, detail=f"Missing required column: {e}") from e
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.post("/predict", 
            tags=["Prediction"],
            summary="Predict anomaly score for online",
            description=FASTAPI_PREDICTION_DESCRIPTION,
            responses=FASTAPI_PREDICTION_RESPONSE,
            response_model=PredictResponse,
            response_description="Prediction result",
            dependencies=[Depends(verify_api_key)])
@limiter.limit("5/minute")
def predict(
    request: Request,
    body: PredictRequest,
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
            threshold=body.threshold,
            feature_cols=feature_cols
        )
        # 予測を実行
        with prediction_latency_seconds.time():
            response = service.predict(dump_request(body))
        # 結果を返却
        return PredictResponse(
                prediction=response["rolling_error"],
                threshold=response["threshold"],
                result=response["result"],
                latency_ms=response["latency_ms"],
                model_version=response["model_version"],
            )
    except HTTPException:
        raise
    except KeyError as e:
        logger.warning("Bad request: missing column %s", e)
        raise HTTPException(status_code=400, detail=f"Missing required column: {e}") from e
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# FastAPI ルーティング xxxに記述する必要あり
app.include_router(router)


