from sqlalchemy.orm import Session
from db.models import PredictionLog

class PredictionLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
            self,
            prediction: float,
            threshold: float,
            result: str,
    ) -> PredictionLog:
        log = PredictionLog(
            prediction=prediction,
            threshold=threshold,
            result=result,
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log