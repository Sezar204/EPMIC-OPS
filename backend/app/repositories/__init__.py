Input
"""Repository layer — thin DB accessors that return ORM objects.

Keeping queries centralised makes services easier to test and lets us
swap in different DBs without rewriting business logic.
"""
from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model: Type[T]

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get(self, id: int) -> Optional[T]:
        return self.db.get(self.model, id)

    def list(self, factory_id: Optional[int] = None, include_deleted: bool = False,
             limit: int = 200, offset: int = 0) -> List[T]:
        stmt = select(self.model)
        if hasattr(self.model, "factory_id") and factory_id is not None:
            stmt = stmt.where(self.model.factory_id == factory_id)
        if hasattr(self.model, "is_deleted") and not include_deleted:
            stmt = stmt.where(self.model.is_deleted == False)  # noqa: E712
        stmt = stmt.order_by(self.model.id).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def add(self, obj: T) -> T:
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, id: int, soft: bool = True) -> bool:
        obj = self.get(id)
        if not obj:
            return False
        if soft and hasattr(obj, "is_deleted"):
            obj.is_deleted = True
            self.db.flush()
        else:
            self.db.delete(obj)
            self.db.flush()
        return True

    def commit(self):
        self.db.commit()
