Input
import logging
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from app.core.config import DB_PATH, BACKUP_DIR, settings
from app.models.system import BackupLog

logger = logging.getLogger(__name__)


class BackupService:
    def create_backup(self, backup_type: str = "auto",
                      external_path: Optional[str] = None) -> dict:
        """Create a SQLite backup using the native backup API.

        Returns a dict with filename, size, status — same shape as
        the BackupLog row written to the DB.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename  = f"emicp_backup_{timestamp}_{backup_type}.db"
        dest      = BACKUP_DIR / filename
        dest.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "filename": filename,
            "backup_type": backup_type,
            "file_size_bytes": 0,
            "file_path": str(dest),
            "status": "success",
            "error_message": None,
            "created_at": datetime.utcnow().isoformat(),
        }

        try:
            src = sqlite3.connect(str(DB_PATH))
            try:
                dst = sqlite3.connect(str(dest))
                try:
                    with dst:
                        src.backup(dst)
                finally:
                    dst.close()
            finally:
                src.close()

            record["file_size_bytes"] = dest.stat().st_size

            if external_path:
                ext = Path(external_path) / filename
                ext.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, ext)

            self._cleanup_old()

        except Exception as e:
            logger.exception("Backup failed")
            record["status"] = "failed"
            record["error_message"] = str(e)

        try:
            from app.core.database import SessionLocal
            db: Session = SessionLocal()
            try:
                log = BackupLog(
                    filename=record["filename"],
                    backup_type=record["backup_type"],
                    file_size_bytes=record["file_size_bytes"],
                    file_path=record["file_path"],
                    status=record["status"],
                    error_message=record["error_message"],
                )
                db.add(log)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Failed to log backup: {e}")

        return record

    def list_backups(self) -> list:
        out: list = []
        for f in sorted(BACKUP_DIR.glob("emicp_backup_*.db"), reverse=True):
            try:
                log = self._find_log(f.name)
                out.append({
                    "filename":      f.name,
                    "backup_type":   (log.backup_type if log else "auto"),
                    "file_size_bytes": f.stat().st_size,
                    "created_at":    (log.created_at.isoformat() if log else
                                      datetime.fromtimestamp(f.stat().st_mtime).isoformat()),
                    "status":        (log.status if log else "success"),
                    "file_path":     str(f),
                })
            except Exception as e:
                logger.warning(f"Skipping corrupt backup entry {f.name}: {e}")
        return out

    def restore_backup(self, filename: str) -> bool:
        src = BACKUP_DIR / filename
        if not src.exists():
            return False
        try:
            self.create_backup("pre_restore")
            shutil.copy2(src, DB_PATH)
            return True
        except Exception as e:
            logger.exception("Restore failed")
            return False

    def _find_log(self, filename: str):
        try:
            from app.core.database import SessionLocal
            db: Session = SessionLocal()
            try:
                return db.query(BackupLog).filter_by(filename=filename).order_by(
                    BackupLog.created_at.desc()
                ).first()
            finally:
                db.close()
        except Exception:
            return None

    def _cleanup_old(self):
        try:
            backups = sorted(BACKUP_DIR.glob("emicp_backup_*.db"),
                             key=lambda p: p.stat().st_mtime, reverse=True)
            for old in backups[settings.BACKUP_KEEP:]:
                old.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Backup cleanup failed: {e}")
