import os
import sys
from pathlib import Path

from pydantic_settings import BaseSettings


def get_app_data_path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    p = base / "EMICP"
    p.mkdir(parents=True, exist_ok=True)
    return p


APP_DATA = get_app_data_path()
DB_PATH = APP_DATA / "data" / "emicp.db"
BACKUP_DIR = APP_DATA / "backups"
EXPORT_DIR = APP_DATA / "exports"
LOG_DIR = APP_DATA / "logs"

for d in [DB_PATH.parent, BACKUP_DIR, EXPORT_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    APP_NAME: str = "EMICP"
    APP_VERSION: str = "1.0.0"
    HOST: str = "127.0.0.1"
    PORT: int = 37210
    DEBUG: bool = False
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    BACKUP_KEEP: int = 30
    AUTO_BACKUP: bool = True
    AUTO_BACKUP_TIME: str = "23:00"
    EXTERNAL_BACKUP_PATH: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
