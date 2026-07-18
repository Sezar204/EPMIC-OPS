"""Generic CRUD + serialization layer.

Implements Repository -> Service style access used by every endpoint router.
All entities are factory-scoped and (where applicable) soft-deleted via an
`is_deleted` flag. Responses are plain dicts keyed by snake_case column names
so they map directly onto the frontend TypeScript interfaces.
"""
from __future__ import annotations

import datetime as dt
from typing import Any, Iterable, Sequence

from sqlalchemy import select, func, or_, String, Integer, Float
from sqlalchemy.orm import Session

from app.core.database import Base


def serialize(obj: Any, seen: set | None = None) -> dict:
    """Convert a SQLAlchemy model instance into a JSON-safe dict."""
    if obj is None:
        return {}
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return {}
    seen.add(id(obj))

    out: dict[str, Any] = {}
    for col in obj.__table__.columns:
        v = getattr(obj, col.name)
        if isinstance(v, (dt.datetime, dt.date)):
            v = v.isoformat()
        out[col.name] = v
    return out


def _has(obj_type: type, attr: str) -> bool:
    return hasattr(obj_type, attr)


def _apply_search(stmt, model, search: str | None, fields: list[str] | None):
    if not search:
        return stmt
    if not fields:
        fields = [c.name for c in model.__table__.columns if isinstance(c.type, (String,))]
    conds = []
    for f in fields:
        if hasattr(model, f):
            col = getattr(model, f)
            conds.append(col.ilike(f"%{search}%"))
    if conds:
        stmt = stmt.where(or_(*conds))
    return stmt


def list_resources(
    db: Session,
    model: type,
    factory_id: int | None = None,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    search_fields: list[str] | None = None,
    filters: dict | None = None,
    order_by: str | None = None,
    descending: bool = False,
    include_deleted: bool = False,
) -> tuple[list[dict], int]:
    stmt = select(model)
    if factory_id is not None and _has(model, "factory_id"):
        stmt = stmt.where(model.factory_id == factory_id)
    if _has(model, "is_deleted") and not include_deleted:
        stmt = stmt.where(model.is_deleted == False)  # noqa: E712
    if filters:
        for k, v in filters.items():
            if v is None:
                continue
            if hasattr(model, k):
                stmt = stmt.where(getattr(model, k) == v)
    stmt = _apply_search(stmt, model, search, search_fields)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    total = total or 0

    if order_by and hasattr(model, order_by):
        col = getattr(model, order_by)
        stmt = stmt.order_by(col.desc() if descending else col.asc())
    else:
        # default: most recent first by id
        if hasattr(model, "id"):
            stmt = stmt.order_by(model.id.desc())

    stmt = stmt.limit(page_size).offset((page - 1) * page_size)
    rows = db.scalars(stmt).all()
    return [serialize(r) for r in rows], total


def get_resource(db: Session, model: type, resource_id: int, factory_id: int | None = None) -> dict | None:
    stmt = select(model).where(model.id == resource_id)
    if factory_id is not None and _has(model, "factory_id"):
        stmt = stmt.where(model.factory_id == factory_id)
    if _has(model, "is_deleted"):
        stmt = stmt.where(model.is_deleted == False)  # noqa: E712
    row = db.scalar(stmt)
    return serialize(row) if row else None


def create_resource(db: Session, model: type, data: dict, factory_id: int | None = None) -> dict:
    payload = {k: v for k, v in data.items() if v is not None}
    if factory_id is not None and _has(model, "factory_id") and "factory_id" not in payload:
        payload["factory_id"] = factory_id
    # drop unknown columns
    cols = {c.name for c in model.__table__.columns}
    payload = {k: v for k, v in payload.items() if k in cols and k != "id"}
    obj = model(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return serialize(obj)


def update_resource(db: Session, model: type, resource_id: int, data: dict, factory_id: int | None = None) -> dict | None:
    stmt = select(model).where(model.id == resource_id)
    if factory_id is not None and _has(model, "factory_id"):
        stmt = stmt.where(model.factory_id == factory_id)
    obj = db.scalar(stmt)
    if not obj:
        return None
    cols = {c.name for c in model.__table__.columns}
    for k, v in data.items():
        if v is None:
            continue
        if k in cols and k != "id":
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return serialize(obj)


def delete_resource(db: Session, model: type, resource_id: int, factory_id: int | None = None) -> bool:
    stmt = select(model).where(model.id == resource_id)
    if factory_id is not None and _has(model, "factory_id"):
        stmt = stmt.where(model.factory_id == factory_id)
    obj = db.scalar(stmt)
    if not obj:
        return False
    if _has(model, "is_deleted"):
        obj.is_deleted = True
        db.commit()
    else:
        db.delete(obj)
        db.commit()
    return True


def bulk_create(db: Session, model: type, rows: list[dict], factory_id: int | None = None) -> int:
    cols = {c.name for c in model.__table__.columns}
    objs = []
    for r in rows:
        payload = {k: v for k, v in r.items() if k in cols and k != "id"}
        if factory_id is not None and _has(model, "factory_id") and "factory_id" not in payload:
            payload["factory_id"] = factory_id
        objs.append(model(**payload))
    db.add_all(objs)
    db.commit()
    return len(objs)
