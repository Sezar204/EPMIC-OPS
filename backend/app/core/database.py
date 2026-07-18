from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
    poolclass=StaticPool,
    echo=settings.DEBUG,
)

try:
    @event.listens_for(engine, "connect")
    def set_pragmas(conn, _):
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA synchronous=NORMAL")
        cur.execute("PRAGMA cache_size=10000")
        cur.close()
except Exception:  # pragma: no cover
    pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import (  # noqa: F401
        factory, production, product, inventory,
        sales, procurement, warehouse, quality,
        maintenance, workforce, cost, kpi, alert, system,
    )
    Base.metadata.create_all(bind=engine)


def check_integrity() -> dict:
    try:
        with engine.connect() as c:
            r = c.execute(text("PRAGMA integrity_check")).fetchone()
            return {"status": "ok" if r and r[0] == "ok" else "corrupted", "issues": []}
    except Exception as e:  # pragma: no cover
        return {"status": "error", "issues": [str(e)]}
