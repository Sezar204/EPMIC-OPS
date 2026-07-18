"""Background scheduler for daily backup and weekly vacuum."""
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.utils.backup import BackupService

_scheduler: BackgroundScheduler | None = None


def _run_backup():
    try:
        BackupService().create_backup("scheduled")
    except Exception as e:  # pragma: no cover
        print(f"[scheduler] backup failed: {e}")


def _run_vacuum():
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(
                __import__("sqlalchemy").text("VACUUM")
            )
    except Exception as e:  # pragma: no cover
        print(f"[scheduler] vacuum failed: {e}")


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    if _scheduler is not None:
        return _scheduler
    try:
        _scheduler = BackgroundScheduler(timezone="UTC")
        hh, mm = (settings.AUTO_BACKUP_TIME + ":00")[:5].split(":")
        if settings.AUTO_BACKUP:
            _scheduler.add_job(
                _run_backup, CronTrigger(hour=int(hh), minute=int(mm)),
                id="daily_backup", replace_existing=True,
            )
        _scheduler.add_job(
            _run_vacuum, CronTrigger(day_of_week="sun", hour=2, minute=0),
            id="weekly_vacuum", replace_existing=True,
        )
        _scheduler.start()
        return _scheduler
    except Exception as e:  # pragma: no cover
        print(f"[scheduler] could not start: {e}")
        return None
