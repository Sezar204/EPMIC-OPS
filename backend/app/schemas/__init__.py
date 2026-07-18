Input
"""Common Pydantic schemas and helpers."""
from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = ""
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    errors: Optional[List[dict]] = None


def ok(data=None, message: str = "OK", **kwargs):
    return ApiResponse(success=True, data=data, message=message, **kwargs)


def err(message: str, errors: Optional[List[dict]] = None):
    return ApiResponse(success=False, data=None, message=message, errors=errors or [])


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=200)
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
