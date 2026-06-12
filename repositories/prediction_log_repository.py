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