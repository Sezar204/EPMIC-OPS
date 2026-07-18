from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EngineResult:
    engine: str
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"engine": self.engine, "success": self.success, "message": self.message, "data": self.data}


class BaseEngine:
    name = "base"

    def execute(self, db, factory_id: int) -> EngineResult:  # pragma: no cover
        raise NotImplementedError

    def _ok(self, message: str, data: dict | None = None) -> EngineResult:
        return EngineResult(self.name, True, message, data or {})

    def _fail(self, message: str, data: dict | None = None) -> EngineResult:
        return EngineResult(self.name, False, message, data or {})
