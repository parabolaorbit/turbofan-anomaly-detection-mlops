from sqlalchemy import Column, Integer, Float, String
from .database import Base
from sqlalchemy import DateTime
from sqlalchemy.sql import func

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    prediction = Column(Float)
    threshold = Column(Float)
    result = Column(String)
    create_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

