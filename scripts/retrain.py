import logging
import subprocess
import sys
from datetime import datetime
from core.logging_config import setup_logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
setup_logging()

def main() -> None:
    logging.info("Retraining batch started.")
    logging.info("Started at: %s", datetime.now().isoformat())

    result = subprocess.run(
        [sys.executable, "-m", "src.train"],
        check=False,
    )

    if result.returncode != 0:
        logging.error("Retraining failed. returncode=%s", result.returncode)
        raise SystemExit(result.returncode)
    
    logging.info("Retraining completed successfully")

    logger.info(
        "retraining_completed",
        extra={
            "extra": {
                "event": "retraining_completed",
                "status": "success",
            }
        },
    )

if __name__ == "__main__":
    main()