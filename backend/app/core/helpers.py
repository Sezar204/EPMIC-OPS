"""Helpers to attach standard CRUD routes for a model onto an APIRouter."""
from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.crud import (
    list_resources, get_resource, create_resource,
    update_resource, delete_resource, serialize,
)
from app.core.response import ok, fail


def add_crud_routes(
    router: APIRouter,
    model: type,
    path: str,
    *,
    search_fields: list[str] | None = None,
    order_by: str | None = None,
    descending: bool = False,
    transform: Callable[[dict, Session, int], Any] | None = None,
) -> None:
    tag = path.replace("/", "_")

    @router.get(f"/{{factory_id}}/{path}")
    def list_route(
        factory_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=200),
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "desc",
        db: Session = Depends(get_db),
    ):
        rows, total = list_resources(
            db, model, factory_id, page=page, page_size=page_size, search=search,
            search_fields=search_fields, order_by=sort_by or order_by,
            descending=(sort_order == "desc") if sort_by else descending,
        )
        if transform:
            rows = [transform(r, db, factory_id) for r in rows]
        return ok(rows, "OK", total=total, page=page, page_size=page_size)

    @router.post(f"/{{factory_id}}/{path}")
    def create_route(factory_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
        obj = create_resource(db, model, data, factory_id)
        return ok(obj, "Created")

    @router.get(f"/{{factory_id}}/{path}/{{rid}}")
    def get_route(factory_id: int, rid: int, db: Session = Depends(get_db)):
        obj = get_resource(db, model, rid, factory_id)
        if not obj:
            return fail("Not found")
        if transform:
            obj = transform(obj, db, factory_id)
        return ok(obj)

    @router.put(f"/{{factory_id}}/{path}/{{rid}}")
    def update_route(factory_id: int, rid: int, data: dict = Body(...), db: Session = Depends(get_db)):
        obj = update_resource(db, model, rid, data, factory_id)
        if not obj:
            return fail("Not found")
        return ok(obj, "Updated")

    @router.delete(f"/{{factory_id}}/{path}/{{rid}}")
    def delete_route(factory_id: int, rid: int, db: Session = Depends(get_db)):
        result = delete_resource(db, model, rid, factory_id)
        if not result:
            return fail("Not found")
        return ok(None, "Deleted")
