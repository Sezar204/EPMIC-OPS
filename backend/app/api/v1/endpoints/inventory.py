Input
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ok
from app.services.operations import InventoryService

router = APIRouter()


@router.get("/raw-materials/{factory_id}")
def raw_materials(factory_id: int, db: Session = Depends(get_db)):
    return ok(InventoryService.raw_materials_view(db, factory_id))


@router.get("/finished-goods/{factory_id}")
def finished_goods(factory_id: int, db: Session = Depends(get_db)):
    return ok(InventoryService.finished_goods_view(db, factory_id))


@router.get("/wip/{factory_id}")
def wip(factory_id: int, db: Session = Depends(get_db)):
    return ok(InventoryService.wip_view(db, factory_id))


@router.get("/analysis/abc-xyz/{factory_id}")
def abc_xyz(factory_id: int, db: Session = Depends(get_db)):
    return ok(InventoryService.abc_xyz(db, factory_id))


@router.get("/analysis/critical-items/{factory_id}")
def critical_items(factory_id: int, db: Session = Depends(get_db)):
    return ok(InventoryService.critical_items(db, factory_id))


@router.get("/analysis/coverage/{factory_id}")
def coverage(factory_id: int, db: Session = Depends(get_db)):
    return ok(InventoryService.coverage_report(db, factory_id))
