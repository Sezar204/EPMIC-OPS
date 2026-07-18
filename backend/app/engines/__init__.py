Input
"""Engines — domain logic that runs analysis, generates alerts,
schedules production, and computes decisions.

Each engine extends BaseEngine and is called from the /engines API
or from the ExecutiveEngine aggregate.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class EngineResult:
    name: str
    success: bool
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    items_processed: int = 0
    alerts_created: int = 0
    decisions_created: int = 0
    notes: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def finish(self):
        self.finished_at = datetime.utcnow()


class BaseEngine:
    name: str = "base"

    def run(self, db: Session, factory_id: int, **kwargs) -> EngineResult:
        r = EngineResult(name=self.name, success=False)
        try:
            self._execute(db, factory_id, r, **kwargs)
            r.success = True
        except Exception as e:
            logger.exception(f"Engine {self.name} failed: {e}")
            r.error = str(e)
        finally:
            r.finish()
            logger.info(
                f"engine={r.name} factory={factory_id} ok={r.success} "
                f"items={r.items_processed} alerts={r.alerts_created} "
                f"elapsed={(r.finished_at - r.started_at).total_seconds():.2f}s"
            )
        return r

    def _execute(self, db: Session, factory_id: int, result: EngineResult, **kwargs):
        raise NotImplementedError
