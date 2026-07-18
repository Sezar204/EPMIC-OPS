import os
import platform
import time
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from app.core.database import get_db, engine, check_integrity
from app.core.config import settings
from app.core.response import ok, fail
from app.utils.backup import BackupService
from app.models.system import AppSetting, BackupLog

router = APIRouter()
_START = time.time()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return ok({
        "database": "connected" if db_ok else "error",
        "version": settings.APP_VERSION,
        "uptime_seconds": int(time.time() - _START),
    }, "System healthy" if db_ok else "DB error")


@router.get("/info")
def info(db: Session = Depends(get_db)):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    backups = db.scalar(select(func.count()).select_from(BackupLog)) or 0
    return ok({
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "os": platform.system(),
        "python": platform.python_version(),
        "db_path": db_path,
        "db_size_bytes": size,
        "backup_count": backups,
    })


@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    rows = db.scalars(select(AppSetting)).all()
    data = {r.key: (r.value or "") for r in rows}
    return ok(data)


@router.put("/settings")
def update_settings(payload: dict, db: Session = Depends(get_db)):
    for k, v in payload.items():
        existing = db.scalar(select(AppSetting).where(AppSetting.key == k))
        if existing:
            existing.value = str(v)
        else:
            db.add(AppSetting(key=k, value=str(v)))
    db.commit()
    return ok(payload, "Settings updated")


@router.post("/backup/now")
def backup_now(db: Session = Depends(get_db)):
    result = BackupService().create_backup("manual")
    return ok(result, "Backup created" if result.get("status") == "success" else "Backup failed")


@router.get("/backup/list")
def backup_list(db: Session = Depends(get_db)):
    rows = db.scalars(select(BackupLog).order_by(BackupLog.created_at.desc())).all()
    return ok([{
        "filename": r.filename, "backup_type": r.backup_type,
        "file_size_bytes": r.file_size_bytes, "created_at": r.created_at.isoformat(),
        "status": r.status, "file_path": r.file_path,
    } for r in rows])


@router.post("/backup/restore/{filename}")
def restore_backup(filename: str, db: Session = Depends(get_db)):
    ok_restore = BackupService().restore_backup(filename)
    if not ok_restore:
        return fail("Restore failed")
    return ok(None, "Restored")


@router.get("/integrity-check")
def integrity(db: Session = Depends(get_db)):
    return ok(check_integrity())
