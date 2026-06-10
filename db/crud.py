from sqlalchemy.orm import Session
from .models import PredictionLog

def  create_prediction_log(
        db: Session,
        prediction: float,
        threshold: float,
        result: str
):
    log = PredictionLog(
        prediction=prediction,
        threshold=threshold,
        result=result
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log
