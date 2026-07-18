"""SQLite backup / restore using the native online-backup API."""
from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select, func

from app.core.config import settings, BACKUP_DIR
from app.core.database import SessionLocal
from app.models.system import BackupLog


def _live_path() -> Path:
    m = re.match(r"sqlite:///(.+)", settings.DATABASE_URL)
    if m:
        return Path(m.group(1))
    return settings.DATABASE_URL.replace("sqlite:///", "")


def _ext_path() -> Path | None:
    p = settings.EXTERNAL_BACKUP_PATH
    if p and Path(p).exists():
        return Path(p)
    return None


class BackupService:
    def create_backup(self, backup_type: str = "manual") -> dict[str, Any]:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"emicp_backup_{stamp}_{backup_type}.db"
        dest = BACKUP_DIR / filename
        live = _live_path()

        size = 0
        status = "success"
        try:
            src = sqlite3.connect(str(live))
            dst = sqlite3.connect(str(dest))
            with dst:
                src.backup(dst)
            src.close()
            dst.close()
            size = dest.stat().st_size
            ext = _ext_path()
            if ext:
                import shutil
                shutil.copy2(dest, ext / filename)
        except Exception as e:  # pragma: no cover
            status = "failed"
            return {"filename": filename, "backup_type": backup_type,
                    "file_size_bytes": 0, "created_at": datetime.now().isoformat(),
                    "status": "failed", "file_path": str(dest), "error": str(e)}

        self._log(filename, backup_type, size, str(dest), status)
        self._cleanup()
        return {
            "filename": filename,
            "backup_type": backup_type,
            "file_size_bytes": size,
            "created_at": datetime.now().isoformat(),
            "status": status,
            "file_path": str(dest),
        }

    def list_backups(self) -> list[dict[str, Any]]:
        results = []
        if not BACKUP_DIR.exists():
            return results
        for f in BACKUP_DIR.glob("*.db"):
            try:
                results.append({
                    "filename": f.name,
                    "backup_type": "manual",
                    "file_size_bytes": f.stat().st_size,
                    "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    "status": "success",
                    "file_path": str(f),
                })
            except Exception:
                continue
        results.sort(key=lambda x: x["created_at"], reverse=True)
        return results

    def restore_backup(self, filename: str) -> bool:
        src = BACKUP_DIR / filename
        if not src.exists():
            return False
        # safety backup first
        try:
            self.create_backup("auto")
        except Exception:
            pass
        live = _live_path()
        try:
            bk = sqlite3.connect(str(src))
            live_conn = sqlite3.connect(str(live))
            with live_conn:
                bk.backup(live_conn)
            bk.close()
            live_conn.close()
            return True
        except Exception:
            return False

    def _log(self, filename, backup_type, size, path, status):
        db = SessionLocal()
        try:
            db.add(BackupLog(filename=filename, backup_type=backup_type,
                             file_size_bytes=size, file_path=path, status=status,
                             created_at=datetime.now()))
            db.commit()
        finally:
            db.close()

    def _cleanup(self):
        keep = settings.BACKUP_KEEP
        backups = self.list_backups()
        for b in backups[keep:]:
            try:
                Path(b["file_path"]).unlink(missing_ok=True)
            except Exception:
                pass
