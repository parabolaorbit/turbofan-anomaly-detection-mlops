import logging
import subprocess
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def run_retraining() -> None:
    logging.info("Scheduled retraining started.")

    result = subprocess.run(
        [sys.executable, "-m", "scripts.retrain"],
        check=False,
    )

    if result.returncode != 0:
        logging.error("Scheduled retraining failed. returncode=%s", result.returncode)
        return
    
    logging.info("Scheduled retraining completed successfully.")

def main() -> None:
    scheduler = BlockingScheduler()

    
    scheduler.add_job(
        run_retraining,
        trigger="cron",
        hour=2,
        minute=0,
    )
    '''
    scheduler.add_job(
        run_retraining,
        trigger="interval",
        minutes=1,
    )
    '''
    logging.info("Scheduler started. Retraining will run daily at 02:00")

    scheduler.start()

if __name__ == "__main__":
    main()