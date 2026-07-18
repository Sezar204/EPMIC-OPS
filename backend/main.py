Input
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings, LOG_DIR
from app.core.database import init_db, check_integrity, SessionLocal
from app.api.v1.router import api_router
from app.utils.backup import BackupService
from app.utils.scheduler import start_scheduler, stop_scheduler
from app.core.seeder import seed_demo_data

log_file = LOG_DIR / "emicp.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(str(log_file), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"EMICP {settings.APP_VERSION} starting...")
    init_db()
    integ = check_integrity()
    if integ["status"] != "ok":
        logger.warning(f"DB integrity: {integ}")
    db = SessionLocal()
    try:
        seed_demo_data(db)
    except Exception as e:
        logger.exception(f"Seed failed: {e}")
    finally:
        db.close()
    try:
        start_scheduler()
    except Exception as e:
        logger.exception(f"Scheduler failed to start: {e}")
    logger.info("EMICP ready.")
    yield
    logger.info("EMICP shutting down...")
    try:
        stop_scheduler()
        BackupService().create_backup("auto")
    except Exception as e:
        logger.error(f"Shutdown backup failed: {e}")
    logger.info("EMICP stopped.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "tauri://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=settings.PORT, reload=False)
