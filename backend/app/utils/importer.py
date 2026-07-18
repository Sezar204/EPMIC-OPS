"""Excel import / template generation (openpyxl — no pandas dependency)."""
from __future__ import annotations

import io
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

from app.core.database import SessionLocal
from app.core.crud import bulk_create
from app.models.production import ProductionLine, Machine, Shift
from app.models.product import Product
from app.models.inventory import RawMaterial
from app.models.procurement import Supplier
from app.models.sales import Customer
from app.models.warehouse import Warehouse
from app.models.sales import SalesOrder
from app.models.procurement import PurchaseOrder

# entity -> model + required fields + header aliases
CONFIG: dict[str, dict[str, Any]] = {
    "production_lines": {
        "model": ProductionLine,
        "required": ["code", "name", "capacity_per_hour"],
        "example": {"code": "PL-NEW", "name": "New Line", "type": "discrete",
                    "capacity_per_hour": 300, "capacity_unit": "units",
                    "status": "active", "changeover_minutes": 15},
    },
    "machines": {
        "model": Machine,
        "required": ["code", "name"],
        "example": {"code": "MC-NEW", "name": "New Machine", "criticality": "medium",
                    "status": "active"},
    },
    "shifts": {
        "model": Shift,
        "required": ["name", "start_time", "end_time"],
        "example": {"name": "Extra", "start_time": "05:00", "end_time": "13:00",
                    "break_minutes": 30, "days_of_week": "1,2,3,4,5", "headcount": 12},
    },
    "products": {
        "model": Product,
        "required": ["sku", "name", "unit_of_measure", "standard_cost", "selling_price"],
        "example": {"sku": "PST-999", "name": "New Product", "category": "Snacks",
                    "unit_of_measure": "pack", "standard_cost": 2.0, "selling_price": 3.5,
                    "type": "finished"},
    },
    "raw_materials": {
        "model": RawMaterial,
        "required": ["code", "name", "unit_of_measure", "standard_cost",
                     "safety_stock_qty", "reorder_point_qty", "lead_time_days"],
        "example": {"code": "RM-999", "name": "New Material", "category": "Ingredient",
                    "unit_of_measure": "kg", "standard_cost": 1.0, "safety_stock_qty": 100,
                    "reorder_point_qty": 60, "lead_time_days": 5},
    },
    "suppliers": {
        "model": Supplier,
        "required": ["code", "name"],
        "example": {"code": "SUP-999", "name": "New Supplier", "rating": 4.0,
                    "status": "active", "payment_terms_days": 30},
    },
    "customers": {
        "model": Customer,
        "required": ["code", "name", "type"],
        "example": {"code": "CUST-999", "name": "New Customer", "type": "b2b",
                    "priority": 3, "payment_terms_days": 30},
    },
    "warehouses": {
        "model": Warehouse,
        "required": ["code", "name", "type"],
        "example": {"code": "WH-999", "name": "New Warehouse", "type": "general",
                    "total_capacity": 1000, "capacity_unit": "sqm"},
    },
    "sales_orders": {
        "model": SalesOrder,
        "required": ["customer_id", "order_number", "required_delivery"],
        "example": {"customer_id": 1, "order_number": "ORD-NEW", "status": "draft",
                    "total_value": 0, "currency": "USD"},
    },
    "purchase_orders": {
        "model": PurchaseOrder,
        "required": ["supplier_id", "po_number", "expected_delivery"],
        "example": {"supplier_id": 1, "po_number": "PO-NEW", "status": "planned",
                    "total_value": 0, "currency": "USD"},
    },
}

NUMERIC = (int, float)


class DataImporter:
    def import_and_validate(self, factory_id: int, entity: str, file_bytes: bytes) -> dict:
        cfg = CONFIG.get(entity)
        if not cfg:
            return {"total": 0, "valid": 0, "errors": [{"row": 0, "message": "Unsupported entity"}], "preview": []}
        model = cfg["model"]
        required = cfg["required"]
        cols = {c.name for c in model.__table__.columns}
        wb = load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return {"total": 0, "valid": 0, "errors": [{"row": 0, "message": "Empty file"}], "preview": []}
        headers = [str(h).strip().lower().replace(" ", "_") if h else "" for h in rows[0]]
        valid, errors, preview = 0, [], []
        for i, row in enumerate(rows[1:], start=2):
            record: dict[str, Any] = {}
            ok = True
            for h, v in zip(headers, row):
                if not h or v is None or v == "":
                    continue
                if h in cols:
                    col = model.__table__.columns[h]
                    try:
                        if isinstance(col.type, (Numeric := __import__("sqlalchemy").Numeric, __import__("sqlalchemy").Integer, __import__("sqlalchemy").Float)):
                            v = float(v) if "." in str(v) or isinstance(v, float) else int(v)
                        elif str(col.type).startswith("BOOLEAN"):
                            v = bool(v)
                    except Exception:
                        errors.append({"row": i, "message": f"Invalid value for {h}"})
                        ok = False
                        break
                    record[h] = v
            if ok:
                missing = [r for r in required if r not in record or record[r] in (None, "")]
                if missing:
                    errors.append({"row": i, "message": f"Missing required: {', '.join(missing)}"})
                    continue
                valid += 1
                if len(preview) < 5:
                    preview.append(record)
            else:
                continue
        return {"total": len(rows) - 1, "valid": valid, "errors": errors[:50], "preview": preview}

    def commit_import(self, factory_id: int, entity: str, valid_rows: list[dict]) -> dict:
        cfg = CONFIG.get(entity)
        if not cfg:
            return {"imported": 0, "skipped": 0, "errors": ["Unsupported entity"]}
        db = SessionLocal()
        try:
            imported = bulk_create(db, cfg["model"], valid_rows, factory_id=factory_id)
            return {"imported": imported, "skipped": 0, "errors": []}
        finally:
            db.close()

    def generate_template(self, entity: str) -> bytes:
        cfg = CONFIG.get(entity)
        if not cfg:
            raise ValueError("Unsupported entity")
        model = cfg["model"]
        wb = Workbook()
        ws = wb.active
        ws.title = entity
        cols = [c.name for c in model.__table__.columns if c.name not in ("id", "created_at", "updated_at", "is_deleted", "factory_id")]
        ws.append(cols)
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=1, column=c)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1E40AF")
            cell.alignment = Alignment(horizontal="center")
        example = cfg["example"]
        ws.append([example.get(c, "") for c in cols])
        out = io.BytesIO()
        wb.save(out)
        return out.getvalue()
