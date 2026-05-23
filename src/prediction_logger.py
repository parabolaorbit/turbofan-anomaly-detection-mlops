import json
from datetime import datetime, timezone
from pathlib import Path

def save_prediction_log(
        log_path: Path,
        input_data: dict,
        prediction_result: dict,
        model_version: str,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
        "input": input_data,
        "prediction": prediction_result,
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_record, ensure_ascii=False) + "\n")
