Input
"""Factories + all master-data + per-factory resources.

This file is large because it hosts the full surface for the
/factories/{id}/* tree. Sub-resources are registered as
APIRouters via _mount().
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.schemas import ok
from app.schemas.factory import (
    FactoryCreate, FactoryUpdate, FactoryRead, FactoryHealthScore,
    FactoryCalendarEntry,
    ProductionLineCreate, ProductionLineUpdate, ProductionLineRead,
    MachineCreate, MachineUpdate, MachineRead,
    ShiftCreate, ShiftUpdate, ShiftRead,
    WarehouseCreate, WarehouseUpdate, WarehouseRead,
)
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductRead,
    RawMaterialCreate, RawMaterialUpdate, RawMaterialRead,
    BOMCreate, BOMUpdate, BOMRead,
)
from app.schemas.sales import (
    CustomerCreate, CustomerUpdate, CustomerRead,
    SalesOrderCreate, SalesOrderUpdate, SalesOrderRead, DemandForecastUpdate,
)
from app.schemas.procurement import SupplierCreate, SupplierUpdate, SupplierRead, POCreate, POUpdate, PORead
from app.services.core import HealthService, DashboardService
from app.services.operations import ProductionService, InventoryService, SalesService
from app.repositories.modules import (
    FactoryRepo, ProductionLineRepo, MachineRepo, ShiftRepo, WarehouseRepo,
    ProductRepo, BOMRepo, RawMaterialRepo, CustomerRepo, SalesOrderRepo,
    DemandForecastRepo, SupplierRepo, PurchaseOrderRepo,
)

router = APIRouter()


# ---------- Factory CRUD ----------
@router.get("/", response_model=None)
def list_factories(db: Session = Depends(get_db)):
    items = FactoryRepo(db).list(include_deleted=False)
    return ok([FactoryRead.model_validate(i).model_dump() for i in items],
              total=len(items))


@router.post("/", response_model=None)
def create_factory(payload: FactoryCreate, db: Session = Depends(get_db)):
    repo = FactoryRepo(db)
    obj = repo.add(Factory(**payload.model_dump()))
    db.commit()
    return ok(FactoryRead.model_validate(obj).model_dump(), "Factory created")


@router.get("/{factory_id}", response_model=None)
def get_factory(factory_id: int, db: Session = Depends(get_db)):
    obj = FactoryRepo(db).get(factory_id)
    if not obj: raise HTTPException(404, "Factory not found")
    return ok(FactoryRead.model_validate(obj).model_dump())


@router.put("/{factory_id}", response_model=None)
def update_factory(factory_id: int, payload: FactoryUpdate, db: Session = Depends(get_db)):
    obj = FactoryRepo(db).get(factory_id)
    if not obj: raise HTTPException(404, "Factory not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    return ok(FactoryRead.model_validate(obj).model_dump(), "Factory updated")


@router.delete("/{factory_id}", response_model=None)
def delete_factory(factory_id: int, db: Session = Depends(get_db)):
    ok_flag = FactoryRepo(db).delete(factory_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Factory not found")
    db.commit()
    return ok(None, "Factory deleted")


@router.get("/{factory_id}/health-score", response_model=None)
def health_score(factory_id: int, db: Session = Depends(get_db)):
    return ok(HealthService.factory_health_score(db, factory_id))


@router.get("/{factory_id}/dashboard-summary", response_model=None)
def dashboard_summary(factory_id: int, db: Session = Depends(get_db)):
    return ok(DashboardService.summary(db, factory_id))


@router.get("/{factory_id}/calendar", response_model=None)
def get_calendar(factory_id: int, month: str, db: Session = Depends(get_db)):
    year, mo = month.split("-")
    from app.models import FactoryCalendar
    from datetime import date as dt
    start = dt(int(year), int(mo), 1)
    if int(mo) == 12:
        end = dt(int(year) + 1, 1, 1)
    else:
        end = dt(int(year), int(mo) + 1, 1)
    items = db.scalars(select(FactoryCalendar).where(
        FactoryCalendar.factory_id == factory_id,
        FactoryCalendar.calendar_date >= start,
        FactoryCalendar.calendar_date < end,
    )).all()
    return ok([{
        "id": i.id, "calendar_date": i.calendar_date.isoformat(),
        "is_working_day": i.is_working_day, "holiday_name": i.holiday_name,
    } for i in items])


@router.post("/{factory_id}/calendar", response_model=None)
def update_calendar(factory_id: int, payload: List[FactoryCalendarEntry],
                    db: Session = Depends(get_db)):
    from app.models import FactoryCalendar
    for entry in payload:
        existing = db.scalars(select(FactoryCalendar).where(
            FactoryCalendar.factory_id == factory_id,
            FactoryCalendar.calendar_date == entry.calendar_date,
        )).first()
        if existing:
            existing.is_working_day = entry.is_working_day
            existing.holiday_name  = entry.holiday_name
        else:
            db.add(FactoryCalendar(
                factory_id=factory_id,
                calendar_date=entry.calendar_date,
                is_working_day=entry.is_working_day,
                holiday_name=entry.holiday_name,
            ))
    db.commit()
    return ok(None, "Calendar updated")


# ---------- Master Data mount helpers ----------
def _factory_or_404(db, factory_id):
    f = FactoryRepo(db).get(factory_id)
    if not f: raise HTTPException(404, "Factory not found")
    return f


# Production Lines
@router.get("/{factory_id}/master-data/production-lines/", response_model=None)
def list_lines(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    items = ProductionLineRepo(db).list(factory_id=factory_id)
    return ok([ProductionLineRead.model_validate(i).model_dump() for i in items], total=len(items))


@router.post("/{factory_id}/master-data/production-lines/", response_model=None)
def create_line(factory_id: int, payload: ProductionLineCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    obj = ProductionLineRepo(db).add(ProductionLine(factory_id=factory_id, **payload.model_dump()))
    db.commit()
    return ok(ProductionLineRead.model_validate(obj).model_dump(), "Line created")


@router.put("/{factory_id}/master-data/production-lines/{line_id}", response_model=None)
def update_line(factory_id: int, line_id: int, payload: ProductionLineUpdate, db: Session = Depends(get_db)):
    obj = ProductionLineRepo(db).get(line_id)
    if not obj: raise HTTPException(404, "Line not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(ProductionLineRead.model_validate(obj).model_dump(), "Line updated")


@router.delete("/{factory_id}/master-data/production-lines/{line_id}", response_model=None)
def delete_line(factory_id: int, line_id: int, db: Session = Depends(get_db)):
    ok_flag = ProductionLineRepo(db).delete(line_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Line not found")
    db.commit()
    return ok(None, "Line deleted")


# Machines
@router.get("/{factory_id}/master-data/machines/", response_model=None)
def list_machines(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    items = MachineRepo(db).list(factory_id=factory_id)
    return ok([MachineRead.model_validate(i).model_dump() for i in items], total=len(items))


@router.post("/{factory_id}/master-data/machines/", response_model=None)
def create_machine(factory_id: int, payload: MachineCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    obj = MachineRepo(db).add(Machine(factory_id=factory_id, **payload.model_dump()))
    db.commit()
    return ok(MachineRead.model_validate(obj).model_dump(), "Machine created")


@router.put("/{factory_id}/master-data/machines/{machine_id}", response_model=None)
def update_machine(factory_id: int, machine_id: int, payload: MachineUpdate, db: Session = Depends(get_db)):
    obj = MachineRepo(db).get(machine_id)
    if not obj: raise HTTPException(404, "Machine not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(MachineRead.model_validate(obj).model_dump(), "Machine updated")


@router.delete("/{factory_id}/master-data/machines/{machine_id}", response_model=None)
def delete_machine(factory_id: int, machine_id: int, db: Session = Depends(get_db)):
    ok_flag = MachineRepo(db).delete(machine_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Machine not found")
    db.commit()
    return ok(None, "Machine deleted")


# Shifts
@router.get("/{factory_id}/master-data/shifts/", response_model=None)
def list_shifts(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    items = ShiftRepo(db).list(factory_id=factory_id)
    return ok([ShiftRead.model_validate(i).model_dump() for i in items], total=len(items))


@router.post("/{factory_id}/master-data/shifts/", response_model=None)
def create_shift(factory_id: int, payload: ShiftCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    obj = ShiftRepo(db).add(Shift(factory_id=factory_id, **payload.model_dump()))
    db.commit()
    return ok(ShiftRead.model_validate(obj).model_dump(), "Shift created")


@router.put("/{factory_id}/master-data/shifts/{shift_id}", response_model=None)
def update_shift(factory_id: int, shift_id: int, payload: ShiftUpdate, db: Session = Depends(get_db)):
    obj = ShiftRepo(db).get(shift_id)
    if not obj: raise HTTPException(404, "Shift not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(ShiftRead.model_validate(obj).model_dump(), "Shift updated")


@router.delete("/{factory_id}/master-data/shifts/{shift_id}", response_model=None)
def delete_shift(factory_id: int, shift_id: int, db: Session = Depends(get_db)):
    ok_flag = ShiftRepo(db).delete(shift_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Shift not found")
    db.commit()
    return ok(None, "Shift deleted")


# Products
@router.get("/{factory_id}/master-data/products/", response_model=None)
def list_products(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    items = ProductRepo(db).list(factory_id=factory_id)
    return ok([ProductRead.model_validate(i).model_dump() for i in items], total=len(items))


@router.post("/{factory_id}/master-data/products/", response_model=None)
def create_product(factory_id: int, payload: ProductCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    obj = ProductRepo(db).add(Product(factory_id=factory_id, **payload.model_dump()))
    db.commit()
    return ok(ProductRead.model_validate(obj).model_dump(), "Product created")


@router.put("/{factory_id}/master-data/products/{product_id}", response_model=None)
def update_product(factory_id: int, product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    obj = ProductRepo(db).get(product_id)
    if not obj: raise HTTPException(404, "Product not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(ProductRead.model_validate(obj).model_dump(), "Product updated")


@router.delete("/{factory_id}/master-data/products/{product_id}", response_model=None)
def delete_product(factory_id: int, product_id: int, db: Session = Depends(get_db)):
    ok_flag = ProductRepo(db).delete(product_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Product not found")
    db.commit()
    return ok(None, "Product deleted")


# BOM
@router.get("/{factory_id}/master-data/bom/", response_model=None)
def list_boms(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    boms = BOMRepo(db).list(factory_id=factory_id)
    out = []
    for b in boms:
        d = BOMRead.model_validate(b).model_dump()
        d["lines"] = [{
            "id": ln.id, "material_id": ln.material_id,
            "quantity_required": ln.quantity_required, "unit": ln.unit,
            "sequence_no": ln.sequence_no, "loss_factor_pct": ln.loss_factor_pct,
        } for ln in (b.lines or [])]
        out.append(d)
    return ok(out, total=len(out))


@router.get("/{factory_id}/master-data/bom/{bom_id}", response_model=None)
def get_bom(factory_id: int, bom_id: int, db: Session = Depends(get_db)):
    obj = BOMRepo(db).get_with_lines(bom_id)
    if not obj: raise HTTPException(404, "BOM not found")
    return ok(BOMRead.model_validate(obj).model_dump())


@router.post("/{factory_id}/master-data/bom/", response_model=None)
def create_bom(factory_id: int, payload: BOMCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    data = payload.model_dump()
    lines = data.pop("lines", [])
    obj = BOMRepo(db).add(BOMHeader(factory_id=factory_id, **data))
    for ln in lines:
        db.add(BOMLine(bom_id=obj.id, **ln))
    db.commit()
    return ok(BOMRead.model_validate(obj).model_dump(), "BOM created")


@router.put("/{factory_id}/master-data/bom/{bom_id}", response_model=None)
def update_bom(factory_id: int, bom_id: int, payload: BOMUpdate, db: Session = Depends(get_db)):
    obj = BOMRepo(db).get(bom_id)
    if not obj: raise HTTPException(404, "BOM not found")
    data = payload.model_dump(exclude_unset=True)
    new_lines = data.pop("lines", None)
    for k, v in data.items(): setattr(obj, k, v)
    if new_lines is not None:
        for ln in list(obj.lines or []):
            db.delete(ln)
        db.flush()
        for ln in new_lines:
            db.add(BOMLine(bom_id=obj.id, **ln))
    db.commit()
    return ok(BOMRead.model_validate(obj).model_dump(), "BOM updated")


@router.delete("/{factory_id}/master-data/bom/{bom_id}", response_model=None)
def delete_bom(factory_id: int, bom_id: int, db: Session = Depends(get_db)):
    ok_flag = BOMRepo(db).delete(bom_id, soft=True)
    if not ok_flag: raise HTTPException(404, "BOM not found")
    db.commit()
    return ok(None, "BOM deleted")


# Raw Materials
@router.get("/{factory_id}/master-data/raw-materials/", response_model=None)
def list_raw_materials(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    items = RawMaterialRepo(db).list(factory_id=factory_id)
    return ok([RawMaterialRead.model_validate(i).model_dump() for i in items], total=len(items))


@router.post("/{factory_id}/master-data/raw-materials/", response_model=None)
def create_raw_material(factory_id: int, payload: RawMaterialCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    obj = RawMaterialRepo(db).add(RawMaterial(factory_id=factory_id, **payload.model_dump()))
    db.commit()
    return ok(RawMaterialRead.model_validate(obj).model_dump(), "Raw material created")


@router.put("/{factory_id}/master-data/raw-materials/{material_id}", response_model=None)
def update_raw_material(factory_id: int, material_id: int, payload: RawMaterialUpdate, db: Session = Depends(get_db)):
    obj = RawMaterialRepo(db).get(material_id)
    if not obj: raise HTTPException(404, "Material not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(RawMaterialRead.model_validate(obj).model_dump(), "Material updated")


@router.delete("/{factory_id}/master-data/raw-materials/{material_id}", response_model=None)
def delete_raw_material(factory_id: int, material_id: int, db: Session = Depends(get_db)):
    ok_flag = RawMaterialRepo(db).delete(material_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Material not found")
    db.commit()
    return ok(None, "Material deleted")


# Suppliers
@router.get("/{factory_id}/master-data/suppliers/", response_model=None)
def list_suppliers(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    items = SupplierRepo(db).list(factory_id=factory_id)
    return ok([SupplierRead.model_validate(i).model_dump() for i in items], total=len(items))


@router.post("/{factory_id}/master-data/suppliers/", response_model=None)
def create_supplier(factory_id: int, payload: SupplierCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    obj = SupplierRepo(db).add(Supplier(factory_id=factory_id, **payload.model_dump()))
    db.commit()
    return ok(SupplierRead.model_validate(obj).model_dump(), "Supplier created")


@router.put("/{factory_id}/master-data/suppliers/{supplier_id}", response_model=None)
def update_supplier(factory_id: int, supplier_id: int, payload: SupplierUpdate, db: Session = Depends(get_db)):
    obj = SupplierRepo(db).get(supplier_id)
    if not obj: raise HTTPException(404, "Supplier not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(SupplierRead.model_validate(obj).model_dump(), "Supplier updated")


@router.delete("/{factory_id}/master-data/suppliers/{supplier_id}", response_model=None)
def delete_supplier(factory_id: int, supplier_id: int, db: Session = Depends(get_db)):
    ok_flag = SupplierRepo(db).delete(supplier_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Supplier not found")
    db.commit()
    return ok(None, "Supplier deleted")


# Customers
@router.get("/{factory_id}/master-data/customers/", response_model=None)
def list_customers(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    items = CustomerRepo(db).list(factory_id=factory_id)
    return ok([CustomerRead.model_validate(i).model_dump() for i in items], total=len(items))


@router.post("/{factory_id}/master-data/customers/", response_model=None)
def create_customer(factory_id: int, payload: CustomerCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    obj = CustomerRepo(db).add(Customer(factory_id=factory_id, **payload.model_dump()))
    db.commit()
    return ok(CustomerRead.model_validate(obj).model_dump(), "Customer created")


@router.put("/{factory_id}/master-data/customers/{customer_id}", response_model=None)
def update_customer(factory_id: int, customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    obj = CustomerRepo(db).get(customer_id)
    if not obj: raise HTTPException(404, "Customer not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(CustomerRead.model_validate(obj).model_dump(), "Customer updated")


@router.delete("/{factory_id}/master-data/customers/{customer_id}", response_model=None)
def delete_customer(factory_id: int, customer_id: int, db: Session = Depends(get_db)):
    ok_flag = CustomerRepo(db).delete(customer_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Customer not found")
    db.commit()
    return ok(None, "Customer deleted")


# Warehouses
@router.get("/{factory_id}/master-data/warehouses/", response_model=None)
def list_warehouses(factory_id: int, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    items = WarehouseRepo(db).list(factory_id=factory_id)
    return ok([WarehouseRead.model_validate(i).model_dump() for i in items], total=len(items))


@router.post("/{factory_id}/master-data/warehouses/", response_model=None)
def create_warehouse(factory_id: int, payload: WarehouseCreate, db: Session = Depends(get_db)):
    _factory_or_404(db, factory_id)
    obj = WarehouseRepo(db).add(Warehouse(factory_id=factory_id, **payload.model_dump()))
    db.commit()
    return ok(WarehouseRead.model_validate(obj).model_dump(), "Warehouse created")


@router.put("/{factory_id}/master-data/warehouses/{warehouse_id}", response_model=None)
def update_warehouse(factory_id: int, warehouse_id: int, payload: WarehouseUpdate, db: Session = Depends(get_db)):
    obj = WarehouseRepo(db).get(warehouse_id)
    if not obj: raise HTTPException(404, "Warehouse not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    db.commit()
    return ok(WarehouseRead.model_validate(obj).model_dump(), "Warehouse updated")


@router.delete("/{factory_id}/master-data/warehouses/{warehouse_id}", response_model=None)
def delete_warehouse(factory_id: int, warehouse_id: int, db: Session = Depends(get_db)):
    ok_flag = WarehouseRepo(db).delete(warehouse_id, soft=True)
    if not ok_flag: raise HTTPException(404, "Warehouse not found")
    db.commit()
    return ok(None, "Warehouse deleted")


# Per-factory alert/decision/kpi routes (mounted under factory context)
@router.get("/{factory_id}/alerts/", response_model=None)
def list_alerts(factory_id: int, db: Session = Depends(get_db)):
    from app.models import Alert
    items = db.scalars(select(Alert).where(Alert.factory_id == factory_id)
                        .order_by(Alert.created_at.desc())).all()
    return ok([{
        "id": a.id, "factory_id": a.factory_id, "alert_type": a.alert_type,
        "severity": a.severity, "title": a.title, "message": a.message,
        "is_read": a.is_read, "is_resolved": a.is_resolved,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    } for a in items], total=len(items))


@router.put("/{factory_id}/alerts/{alert_id}/read", response_model=None)
def mark_alert_read(factory_id: int, alert_id: int, db: Session = Depends(get_db)):
    from app.models import Alert
    a = db.get(Alert, alert_id)
    if not a: raise HTTPException(404, "Alert not found")
    a.is_read = True
    db.commit()
    return ok(None, "Alert marked read")


@router.put("/{factory_id}/alerts/{alert_id}/resolve", response_model=None)
def resolve_alert(factory_id: int, alert_id: int, db: Session = Depends(get_db)):
    from app.models import Alert
    a = db.get(Alert, alert_id)
    if not a: raise HTTPException(404, "Alert not found")
    a.is_resolved = True
    a.resolved_at = __import__("datetime").datetime.utcnow()
    db.commit()
    return ok(None, "Alert resolved")


@router.get("/{factory_id}/decisions/pending", response_model=None)
def pending_decisions(factory_id: int, db: Session = Depends(get_db)):
    from app.models import Decision
    items = db.scalars(select(Decision).where(
        Decision.factory_id == factory_id, Decision.status == "pending",
    ).order_by(Decision.priority.desc(), Decision.created_at.desc())).all()
    return ok([{
        "id": d.id, "factory_id": d.factory_id, "decision_type": d.decision_type,
        "title": d.title, "description": d.description,
        "recommendation": d.recommendation,
        "impact_summary": d.impact_summary,
        "status": d.status, "priority": d.priority,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    } for d in items], total=len(items))


@router.put("/{factory_id}/decisions/{decision_id}/approve", response_model=None)
def approve_decision(factory_id: int, decision_id: int, db: Session = Depends(get_db)):
    from app.models import Decision
    from datetime import datetime
    d = db.get(Decision, decision_id)
    if not d: raise HTTPException(404, "Decision not found")
    d.status = "approved"
    d.decided_at = datetime.utcnow()
    db.commit()
    return ok(None, "Decision approved")


@router.put("/{factory_id}/decisions/{decision_id}/reject", response_model=None)
def reject_decision(factory_id: int, decision_id: int, payload: dict, db: Session = Depends(get_db)):
    from app.models import Decision
    from datetime import datetime
    d = db.get(Decision, decision_id)
    if not d: raise HTTPException(404, "Decision not found")
    d.status = "rejected"
    d.decided_at = datetime.utcnow()
    d.decision_notes = payload.get("notes", "")
    db.commit()
    return ok(None, "Decision rejected")


@router.get("/{factory_id}/kpis/", response_model=None)
def list_kpis(factory_id: int, db: Session = Depends(get_db)):
    from app.models import KPIDefinition, KPIValue
    from datetime import date as dt, timedelta
    defs = db.scalars(select(KPIDefinition).where(
        KPIDefinition.factory_id == factory_id, KPIDefinition.is_active == True  # noqa: E712
    )).all()
    out = []
    cutoff = dt.today() - timedelta(days=30)
    for d in defs:
        trend = db.scalars(select(KPIValue).where(
            KPIValue.kpi_id == d.id, KPIValue.factory_id == factory_id,
            KPIValue.period_date >= cutoff,
        ).order_by(KPIValue.period_date.asc())).all()
        values = [v.value for v in trend]
        latest = values[-1] if values else 0
        prev   = values[-2] if len(values) > 1 else latest
        change = latest - prev
        out.append({
            "id": d.id, "code": d.code, "name": d.name, "category": d.category,
            "unit": d.unit, "target_value": d.target_value,
            "warning_threshold": d.warning_threshold,
            "critical_threshold": d.critical_threshold,
            "higher_is_better": d.higher_is_better,
            "display_format": d.display_format,
            "value": latest, "previous_value": prev, "change": round(change, 2),
            "trend": values,
        })
    return ok(out, total=len(out))


@router.get("/{factory_id}/kpis/{category}", response_model=None)
def kpis_by_category(factory_id: int, category: str, db: Session = Depends(get_db)):
    from app.models import KPIDefinition
    items = db.scalars(select(KPIDefinition).where(
        KPIDefinition.factory_id == factory_id, KPIDefinition.category == category,
        KPIDefinition.is_active == True,  # noqa: E712
    )).all()
    return ok([{"id": i.id, "code": i.code, "name": i.name} for i in items], total=len(items))


@router.post("/{factory_id}/kpis/custom/", response_model=None)
def create_custom_kpi(factory_id: int, payload: dict, db: Session = Depends(get_db)):
    from app.models import KPIDefinition
    obj = KPIDefinition(factory_id=factory_id, is_custom=True, **payload)
    db.add(obj); db.commit(); db.refresh(obj)
    return ok({"id": obj.id}, "Custom KPI created")
