from sqlalchemy import Column, Integer, Float, String
from .database import Base
from sqlalchemy import DateTime, Boolean
from sqlalchemy.sql import func

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    prediction = Column(Float)
    threshold = Column(Float)
    result = Column(String)  
    unit_number = Column(Integer)
    severity = Column(String)   
    alert = Column(Boolean)
    final_alert = Column(Boolean)
    latency_ms = Column(Float)
    sensor_ms2_mean = Column(Float)
    sensor_ms3_mean = Column(Float)
    sensor_ms4_mean = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

