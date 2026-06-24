from sqlalchemy.orm import Session
from db.models import PredictionLog

class PredictionLogRepository:
    """
    ログをDBに書き込むためのModelインスタンスを生成
    """
    def __init__(self, db: Session):
        self.db = db

    def create(
            self,
            **fields,
    ) -> PredictionLog:
        log = PredictionLog(
            **fields
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log
    
    def get_recent_logs(
        self,
        limit: int = 20
    ) -> PredictionLog:
        logs = self.db.query(PredictionLog) \
        .order_by(PredictionLog.created_at.desc()) \
        .limit(limit) \
        .all()
        return logs
    
    def get_recent_anomalies(
        self,
        limit: int = 20
    ) -> PredictionLog:
        logs = self.db.query(PredictionLog) \
        .filter(PredictionLog.result == "anomaly") \
        .order_by(PredictionLog.create_at.desc()) \
        .limit(limit) \
        .all()
        return logs
    
    def count_predictions(self):
        return self.db.query(PredictionLog).count()
    
    def count_anomalies(self):
        logs = self.db.query(PredictionLog) \
        .filter(PredictionLog.result == "anomaly") \
        .count()
        return logs