Input
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.config import LOG_DIR
from app.utils.backup import BackupService
from app.core.database import engine
from sqlalchemy import text

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _daily_backup():
    try:
        BackupService().create_backup("scheduled")
        logger.info("Scheduled daily backup complete")
    except Exception as e:
        logger.exception(f"Scheduled backup failed: {e}")


def _weekly_vacuum():
    try:
        with engine.connect() as c:
            c.execute(text("VACUUM"))
            c.execute(text("ANALYZE"))
            c.commit()
        logger.info("Weekly VACUUM + ANALYZE complete")
    except Exception as e:
        logger.exception(f"Weekly vacuum failed: {e}")


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler:
        return _scheduler

    sched = BackgroundScheduler(timezone="UTC")
    sched.add_job(_daily_backup,  "cron", hour=23, minute=0,  id="daily_backup")
    sched.add_job(_weekly_vacuum, "cron", day_of_week="sun", hour=2, minute=0, id="weekly_vacuum")
    sched.start()
    _scheduler = sched
    logger.info(f"Scheduler started (logs: {LOG_DIR})")
    return sched


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
