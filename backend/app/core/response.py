"""Response envelope helpers used by every endpoint."""
from typing import Any


def ok(
    data: Any = None,
    message: str = "OK",
    total: int | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> dict:
    resp: dict[str, Any] = {
        "success": True,
        "data": data,
        "message": message,
    }
    if total is not None:
        resp["total"] = total
    if page is not None:
        resp["page"] = page
    if page_size is not None:
        resp["page_size"] = page_size
    return resp


def fail(message: str, errors: list[dict] | None = None, data: Any = None) -> dict:
    return {
        "success": False,
        "data": data,
        "message": message,
        "errors": errors or [],
    }
