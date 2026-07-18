Input
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db, check_integrity
from app.schemas import ok
from app.services.core import SystemInfoService, SettingsService
from app.utils.backup import BackupService

router = APIRouter()


@router.get("/health")
def health():
    integ = check_integrity()
    return ok({"db": integ["status"]})


@router.get("/info")
def info(db: Session = Depends(get_db)):
    return ok(SystemInfoService.info(db))


@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    return ok(SettingsService.get_all(db))


@router.put("/settings")
def update_settings(payload: dict, db: Session = Depends(get_db)):
    return ok(SettingsService.update(db, payload), "Settings updated")


@router.post("/backup/now")
def backup_now():
    rec = BackupService().create_backup("manual")
    return ok(rec, "Backup created" if rec["status"] == "success" else "Backup failed")


@router.get("/backup/list")
def list_backups():
    return ok(BackupService().list_backups())


@router.post("/backup/restore/{filename}")
def restore(filename: str):
    ok_flag = BackupService().restore_backup(filename)
    if not ok_flag:
        return ok(None, "Restore failed")
    return ok(None, "Restored — please restart the app")


@router.get("/integrity-check")
def integrity():
    return ok(check_integrity())
