"""Demo data seeder. Runs only when the factories table is empty."""
from __future__ import annotations

import datetime as dt
import random

from sqlalchemy import select, func

from app.core.database import SessionLocal
from app.models import (
    Factory, FactoryCalendar, ProductionLine, Machine, Shift, ProductionOrder,
    Product, BOMHeader, BOMLine, RawMaterial, InventoryRawMaterial,
    InventoryFinishedGoods, InventoryWIP, Customer, SalesOrder, SalesOrderLine,
    DemandForecast, Supplier, SupplierMaterial, PurchaseOrder, PurchaseOrderLine,
    Warehouse, QualityCheck, NonConformanceReport, CAPARecord, MaintenanceSchedule,
    MaintenanceWorkOrder, MachineBreakdown, Worker, ShiftAssignment, AttendanceRecord,
    ProductCost, KPIDefinition, KPIValue, Alert, Decision, BackupLog, AppSetting,
)


def _today() -> dt.date:
    return dt.date.today()


def _now() -> dt.datetime:
    return dt.datetime.utcnow()


def _days_ago(n: int) -> dt.datetime:
    return _now() - dt.timedelta(days=n)


def _days_ahead(n: int) -> dt.datetime:
    return _now() + dt.timedelta(days=n)


def seed_demo_data(db) -> None:
    count = db.scalar(select(func.count()).select_from(Factory))
    if count and count > 0:
        return

    random.seed(42)

    # ---- Factory ----
    factory = Factory(
        code="CAIRO-01", name="Cairo Manufacturing Plant", type="hybrid",
        status="active", location="Cairo, Egypt", currency="EGP",
        timezone="Africa/Cairo", working_start="08:00", working_end="18:00",
        notes="Flagship plant — snacks, beverages and confectionery.",
    )
    db.add(factory)
    db.flush()

    fid = factory.id

    # Working calendar for current + next month
    today = _today()
    for d in range(-10, 40):
        day = today + dt.timedelta(days=d)
        is_weekend = day.weekday() >= 5
        db.add(FactoryCalendar(
            factory_id=fid, cal_date=day,
            is_working_day=not is_weekend, is_holiday=False,
        ))

    # ---- Production lines ----
    pl_pkg = ProductionLine(factory_id=fid, code="PL-PKG", name="Packaging Line",
                            type="discrete", capacity_per_hour=500, capacity_unit="units",
                            status="active", changeover_minutes=20)
    pl_asm = ProductionLine(factory_id=fid, code="PL-ASM", name="Assembly Line",
                            type="discrete", capacity_per_hour=200, capacity_unit="units",
                            status="active", changeover_minutes=30)
    pl_prc = ProductionLine(factory_id=fid, code="PL-PRC", name="Processing Line",
                            type="process", capacity_per_hour=1000, capacity_unit="kg",
                            status="active", changeover_minutes=45)
    db.add_all([pl_pkg, pl_asm, pl_prc])
    db.flush()

    # ---- Machines ----
    machines = [
        Machine(factory_id=fid, line_id=pl_pkg.id, code="PKG-01", name="Packaging Line A",
                type="Flow wrapper", capacity=500, capacity_unit="units/h",
                criticality="high", status="active"),
        Machine(factory_id=fid, line_id=pl_pkg.id, code="PKG-02", name="Carton Sealer",
                capacity=400, capacity_unit="units/h", criticality="medium", status="active"),
        Machine(factory_id=fid, line_id=pl_asm.id, code="ASM-01", name="Robotic Arm",
                type="Pick & place", capacity=220, capacity_unit="units/h",
                criticality="critical", status="active"),
        Machine(factory_id=fid, line_id=pl_asm.id, code="ASM-02", name="Conveyor",
                capacity=250, capacity_unit="units/h", criticality="medium", status="idle"),
        Machine(factory_id=fid, line_id=pl_prc.id, code="PRC-01", name="Mixer",
                type="Batch mixer", capacity=1200, capacity_unit="kg/h",
                criticality="critical", status="active"),
        Machine(factory_id=fid, line_id=pl_prc.id, code="PRC-02", name="Reactor",
                type="Thermal reactor", capacity=900, capacity_unit="kg/h",
                criticality="high", status="maintenance"),
        Machine(factory_id=fid, line_id=pl_prc.id, code="PRC-03", name="Filler",
                capacity=1000, capacity_unit="kg/h", criticality="medium", status="active"),
        Machine(factory_id=fid, code="GEN-01", name="Air Compressor",
                type="Utility", criticality="low", status="down"),
    ]
    db.add_all(machines)
    db.flush()

    # ---- Shifts ----
    shifts = [
        Shift(factory_id=fid, name="Morning", start_time="06:00", end_time="14:00",
              break_minutes=30, days_of_week="1,2,3,4,5", headcount=20, is_active=True),
        Shift(factory_id=fid, name="Afternoon", start_time="14:00", end_time="22:00",
              break_minutes=30, days_of_week="1,2,3,4,5", headcount=15, is_active=True),
        Shift(factory_id=fid, name="Night", start_time="22:00", end_time="06:00",
              break_minutes=45, days_of_week="1,2,3,4,5", headcount=10, is_active=True),
    ]
    db.add_all(shifts)
    db.flush()

    # ---- Products ----
    products = [
        Product(factory_id=fid, sku="PST-001", name="Premium Snack Pack", category="Snacks",
                unit_of_measure="pack", standard_cost=2.5, selling_price=4.5, min_order_qty=100,
                lead_time_days=2, type="finished"),
        Product(factory_id=fid, sku="PST-002", name="Family Snack Pack", category="Snacks",
                unit_of_measure="pack", standard_cost=4.0, selling_price=6.9, min_order_qty=50,
                lead_time_days=2, type="finished"),
        Product(factory_id=fid, sku="SEM-001", name="Seasoning Mix", category="Semi",
                unit_of_measure="kg", standard_cost=1.2, selling_price=1.8, min_order_qty=50,
                lead_time_days=1, type="semi-finished"),
        Product(factory_id=fid, sku="SEM-002", name="Syrup Base", category="Semi",
                unit_of_measure="L", standard_cost=0.8, selling_price=1.2, min_order_qty=50,
                lead_time_days=1, type="semi-finished"),
        Product(factory_id=fid, sku="PST-003", name="Bottled Drink 500ml", category="Beverages",
                unit_of_measure="bottle", standard_cost=0.6, selling_price=1.2, min_order_qty=500,
                lead_time_days=1, type="finished"),
        Product(factory_id=fid, sku="PST-004", name="Bottled Drink 1L", category="Beverages",
                unit_of_measure="bottle", standard_cost=1.1, selling_price=2.0, min_order_qty=300,
                lead_time_days=1, type="finished"),
        Product(factory_id=fid, sku="PST-005", name="Granola Bar", category="Snacks",
                unit_of_measure="bar", standard_cost=1.5, selling_price=2.8, min_order_qty=200,
                lead_time_days=2, type="finished"),
        Product(factory_id=fid, sku="SEM-003", name="Filling Paste", category="Semi",
                unit_of_measure="kg", standard_cost=2.0, selling_price=3.0, min_order_qty=40,
                lead_time_days=1, type="semi-finished"),
        Product(factory_id=fid, sku="PST-006", name="Chocolate Coated", category="Confectionery",
                unit_of_measure="box", standard_cost=3.0, selling_price=5.5, min_order_qty=80,
                lead_time_days=3, type="finished"),
        Product(factory_id=fid, sku="PST-007", name="Gift Bundle", category="Snacks",
                unit_of_measure="pack", standard_cost=5.0, selling_price=9.9, min_order_qty=30,
                lead_time_days=3, type="finished"),
    ]
    db.add_all(products)
    db.flush()
    by_sku = {p.sku: p for p in products}

    # ---- Raw materials ----
    rms = [
        RawMaterial(factory_id=fid, code="RM-001", name="Plastic Film", category="Packaging",
                    unit_of_measure="kg", standard_cost=1.2, safety_stock_qty=200, reorder_point_qty=150, lead_time_days=7),
        RawMaterial(factory_id=fid, code="RM-002", name="Carton Box", category="Packaging",
                    unit_of_measure="each", standard_cost=0.3, safety_stock_qty=500, reorder_point_qty=300, lead_time_days=5),
        RawMaterial(factory_id=fid, code="RM-003", name="Wheat Flour", category="Ingredient",
                    unit_of_measure="kg", standard_cost=0.5, safety_stock_qty=1000, reorder_point_qty=600, lead_time_days=4),
        RawMaterial(factory_id=fid, code="RM-004", name="Sugar", category="Ingredient",
                    unit_of_measure="kg", standard_cost=0.4, safety_stock_qty=800, reorder_point_qty=500, lead_time_days=3),
        RawMaterial(factory_id=fid, code="RM-005", name="Palm Oil", category="Ingredient",
                    unit_of_measure="kg", standard_cost=0.7, safety_stock_qty=400, reorder_point_qty=250, lead_time_days=6),
        RawMaterial(factory_id=fid, code="RM-006", name="Salt", category="Ingredient",
                    unit_of_measure="kg", standard_cost=0.1, safety_stock_qty=300, reorder_point_qty=200, lead_time_days=2),
        RawMaterial(factory_id=fid, code="RM-007", name="Cocoa Powder", category="Ingredient",
                    unit_of_measure="kg", standard_cost=2.5, safety_stock_qty=100, reorder_point_qty=60, lead_time_days=10),
        RawMaterial(factory_id=fid, code="RM-008", name="Vanilla Flavor", category="Flavor",
                    unit_of_measure="kg", standard_cost=5.0, safety_stock_qty=20, reorder_point_qty=10, lead_time_days=14),
        RawMaterial(factory_id=fid, code="RM-009", name="Preservative", category="Additive",
                    unit_of_measure="kg", standard_cost=1.5, safety_stock_qty=50, reorder_point_qty=30, lead_time_days=7),
        RawMaterial(factory_id=fid, code="RM-010", name="Coloring", category="Additive",
                    unit_of_measure="kg", standard_cost=1.0, safety_stock_qty=30, reorder_point_qty=15, lead_time_days=7),
        RawMaterial(factory_id=fid, code="RM-011", name="Nuts", category="Ingredient",
                    unit_of_measure="kg", standard_cost=3.0, safety_stock_qty=80, reorder_point_qty=50, lead_time_days=9),
        RawMaterial(factory_id=fid, code="RM-012", name="Water", category="Ingredient",
                    unit_of_measure="L", standard_cost=0.05, safety_stock_qty=2000, reorder_point_qty=1000, lead_time_days=1),
        RawMaterial(factory_id=fid, code="RM-013", name="Bottle PET 500", category="Packaging",
                    unit_of_measure="each", standard_cost=0.08, safety_stock_qty=5000, reorder_point_qty=3000, lead_time_days=5),
        RawMaterial(factory_id=fid, code="RM-014", name="Bottle PET 1L", category="Packaging",
                    unit_of_measure="each", standard_cost=0.12, safety_stock_qty=3000, reorder_point_qty=2000, lead_time_days=5),
        RawMaterial(factory_id=fid, code="RM-015", name="Cap", category="Packaging",
                    unit_of_measure="each", standard_cost=0.03, safety_stock_qty=6000, reorder_point_qty=4000, lead_time_days=5),
    ]
    db.add_all(rms)
    db.flush()
    by_rm = {r.code: r for r in rms}

    # ---- BOMs ----
    def add_bom(sku: str, name: str, lines: list[tuple[str, float, str, float]]):
        prod = by_sku[sku]
        bom = BOMHeader(factory_id=fid, product_id=prod.id, version="1.0", name=name,
                        status="active", yield_pct=98.0, effective_date=_today())
        db.add(bom)
        db.flush()
        for seq, (rm_code, qty, unit, loss) in enumerate(lines, start=1):
            rm = by_rm[rm_code]
            db.add(BOMLine(bom_id=bom.id, material_id=rm.id, quantity_required=qty,
                           unit=unit, loss_factor_pct=loss, is_alternative=False,
                           sequence_no=seq))

    add_bom("PST-001", "Premium Snack Pack BOM", [
        ("RM-003", 0.40, "kg", 2), ("RM-004", 0.15, "kg", 1), ("RM-005", 0.10, "kg", 1),
        ("RM-001", 0.05, "kg", 1), ("RM-009", 0.01, "kg", 0),
    ])
    add_bom("PST-002", "Family Snack Pack BOM", [
        ("RM-003", 0.80, "kg", 2), ("RM-004", 0.30, "kg", 1), ("RM-005", 0.20, "kg", 1),
        ("RM-002", 1, "each", 0), ("RM-009", 0.02, "kg", 0),
    ])
    add_bom("SEM-001", "Seasoning Mix BOM", [
        ("RM-006", 0.30, "kg", 1), ("RM-008", 0.02, "kg", 0), ("RM-010", 0.01, "kg", 0),
        ("RM-009", 0.01, "kg", 0),
    ])
    add_bom("SEM-002", "Syrup Base BOM", [
        ("RM-004", 0.50, "kg", 1), ("RM-012", 0.40, "L", 0), ("RM-008", 0.03, "kg", 0),
    ])
    add_bom("PST-003", "Bottled Drink 500ml BOM", [
        ("RM-012", 0.45, "L", 1), ("RM-010", 0.005, "kg", 0), ("RM-013", 1, "each", 0),
        ("RM-015", 1, "each", 0),
    ])
    add_bom("PST-004", "Bottled Drink 1L BOM", [
        ("RM-012", 0.95, "L", 1), ("RM-010", 0.01, "kg", 0), ("RM-014", 1, "each", 0),
        ("RM-015", 1, "each", 0),
    ])
    add_bom("PST-005", "Granola Bar BOM", [
        ("RM-003", 0.35, "kg", 2), ("RM-004", 0.10, "kg", 1), ("RM-011", 0.20, "kg", 1),
        ("RM-001", 0.04, "kg", 1),
    ])
    add_bom("SEM-003", "Filling Paste BOM", [
        ("RM-004", 0.40, "kg", 1), ("RM-007", 0.15, "kg", 1), ("RM-005", 0.10, "kg", 1),
    ])
    add_bom("PST-006", "Chocolate Coated BOM", [
        ("RM-007", 0.25, "kg", 2), ("RM-003", 0.30, "kg", 1), ("RM-004", 0.10, "kg", 1),
        ("RM-002", 1, "each", 0),
    ])
    add_bom("PST-007", "Gift Bundle BOM", [
        ("RM-003", 0.50, "kg", 1), ("RM-007", 0.10, "kg", 1), ("RM-002", 1, "each", 0),
    ])

    # ---- Suppliers + links ----
    suppliers = [
        Supplier(factory_id=fid, code="SUP-001", name="Global Ingredients", contact_name="Ahmed",
                 contact_email="ahmed@gig.com", rating=4.5, status="active", payment_terms_days=30),
        Supplier(factory_id=fid, code="SUP-002", name="PackCorp", contact_name="Laila",
                 contact_email="laila@packcorp.com", rating=4.0, status="active", payment_terms_days=45),
        Supplier(factory_id=fid, code="SUP-003", name="FlavorHouse", contact_name="Samir",
                 contact_email="samir@flavorhouse.com", rating=3.5, status="active", payment_terms_days=60),
        Supplier(factory_id=fid, code="SUP-004", name="NutFarm", contact_name="Mona",
                 contact_email="mona@nutfarm.com", rating=4.8, status="active", payment_terms_days=30),
        Supplier(factory_id=fid, code="SUP-005", name="ChemSupply", contact_name="Tarek",
                 contact_email="tarek@chemsupply.com", rating=3.0, status="active", payment_terms_days=30),
    ]
    db.add_all(suppliers)
    db.flush()
    sup_by_code = {s.code: s for s in suppliers}

    # preferred supplier links
    links = [
        ("SUP-001", "RM-003"), ("SUP-001", "RM-004"), ("SUP-001", "RM-005"), ("SUP-001", "RM-006"),
        ("SUP-002", "RM-001"), ("SUP-002", "RM-002"), ("SUP-002", "RM-013"), ("SUP-002", "RM-014"), ("SUP-002", "RM-015"),
        ("SUP-003", "RM-008"), ("SUP-003", "RM-010"),
        ("SUP-004", "RM-011"), ("SUP-004", "RM-007"),
        ("SUP-005", "RM-009"), ("SUP-005", "RM-012"),
    ]
    for sc, mc in links:
        db.add(SupplierMaterial(factory_id=fid, supplier_id=sup_by_code[sc].id,
                                material_id=by_rm[mc].id, is_preferred=True,
                                lead_time_days=by_rm[mc].lead_time_days,
                                unit_price=by_rm[mc].standard_cost))

    # ---- Customers ----
    customers = [
        Customer(factory_id=fid, code="CUST-001", name="MegaMart", type="b2b", priority=5,
                 credit_limit=500000, payment_terms_days=30, contact_name="Omar"),
        Customer(factory_id=fid, code="CUST-002", name="RetailChain", type="distributor", priority=4,
                 credit_limit=800000, payment_terms_days=45, contact_name="Hana"),
        Customer(factory_id=fid, code="CUST-003", name="CafeSupply", type="b2b", priority=3,
                 credit_limit=200000, payment_terms_days=30, contact_name="Yara"),
        Customer(factory_id=fid, code="CUST-004", name="ExportTrader", type="b2b", priority=4,
                 credit_limit=600000, payment_terms_days=60, contact_name="Khaled"),
        Customer(factory_id=fid, code="CUST-005", name="LocalShop", type="b2c", priority=2,
                 credit_limit=50000, payment_terms_days=15, contact_name="Sara"),
    ]
    db.add_all(customers)
    db.flush()
    cust_by_code = {c.code: c for c in customers}

    # ---- Warehouse ----
    wh = Warehouse(factory_id=fid, code="WH-001", name="Main Warehouse", type="general",
                   total_capacity=5000, capacity_unit="sqm", storage_conditions="Ambient, dry",
                   location="Cairo Plant")
    db.add(wh)
    db.flush()
    wh_id = wh.id

    # ---- Inventory (raw materials) ----
    # explicit on-hand to create critical/healthy mix
    inv_levels = {
        "RM-001": 180, "RM-002": 600, "RM-003": 1200, "RM-004": 900, "RM-005": 300,
        "RM-006": 250, "RM-007": 40, "RM-008": 8, "RM-009": 60, "RM-010": 35,
        "RM-011": 70, "RM-012": 2500, "RM-013": 5200, "RM-014": 3100, "RM-015": 0,
    }
    for code, on_hand in inv_levels.items():
        rm = by_rm[code]
        reserved = round(on_hand * 0.15)
        db.add(InventoryRawMaterial(
            factory_id=fid, material_id=rm.id, warehouse_id=wh_id,
            qty_on_hand=on_hand, qty_reserved=reserved, qty_available=max(0, on_hand - reserved),
            batch_number=f"B-{code}", last_movement=_today() - dt.timedelta(days=random.randint(1, 6)),
        ))

    # ---- Inventory finished goods ----
    for sku in ["PST-001", "PST-002", "PST-003", "PST-004", "PST-005", "PST-006"]:
        p = by_sku[sku]
        on_hand = random.randint(300, 1500)
        reserved = round(on_hand * 0.2)
        db.add(InventoryFinishedGoods(
            factory_id=fid, product_id=p.id, warehouse_id=wh_id,
            qty_on_hand=on_hand, qty_reserved=reserved, qty_available=on_hand - reserved,
            batch_number=f"FG-{sku}", last_updated=_now(),
        ))

    # ---- Sales orders ----
    so_specs = [
        ("CUST-001", "PST-001", 800, "confirmed", 5),
        ("CUST-002", "PST-003", 5000, "in_production", 6),
        ("CUST-003", "PST-005", 1200, "ready", 3),
        ("CUST-004", "PST-006", 400, "confirmed", 1),
        ("CUST-005", "PST-002", 200, "draft", 12),
    ]
    for i, (cc, sku, qty, status, due_in) in enumerate(so_specs, start=1):
        cust = cust_by_code[cc]
        prod = by_sku[sku]
        order_date = _days_ago(random.randint(2, 20))
        unit = prod.selling_price
        line_total = qty * unit
        so = SalesOrder(
            factory_id=fid, customer_id=cust.id, order_number=f"ORD-2026{str(i).zfill(4)}",
            order_date=order_date, required_delivery=_days_ahead(due_in),
            status=status, total_value=line_total, currency="EGP",
            is_rush_order=(status == "confirmed" and due_in <= 3),
            priority=cust.priority,
        )
        db.add(so)
        db.flush()
        db.add(SalesOrderLine(
            order_id=so.id, product_id=prod.id, quantity=qty, unit_price=unit,
            discount_pct=0, line_total=line_total, required_date=_days_ahead(due_in),
            status="open", fulfilled_qty=round(qty * 0.4) if status in ("in_production", "ready") else 0,
        ))

    # ---- Purchase orders (1 overdue) ----
    po_specs = [
        ("SUP-001", "RM-003", 1000, "received", -20),
        ("SUP-002", "RM-013", 5000, "in_transit", -2),
        ("SUP-004", "RM-007", 120, "issued", 12),
    ]
    for i, (sc, rm_code, qty, status, days) in enumerate(po_specs, start=1):
        sup = sup_by_code[sc]
        rm = by_rm[rm_code]
        expected = _days_ahead(days) if days >= 0 else _days_ago(-days)
        total = qty * rm.standard_cost
        po = PurchaseOrder(
            factory_id=fid, supplier_id=sup.id, po_number=f"PO-2026{str(i).zfill(4)}",
            order_date=_days_ago(abs(days) + 5), expected_delivery=expected,
            status=status, total_value=total, currency="EGP",
        )
        db.add(po)
        db.flush()
        db.add(PurchaseOrderLine(
            po_id=po.id, material_id=rm.id, qty_ordered=qty, unit_price=rm.standard_cost,
            qty_received=qty if status == "received" else 0,
            quality_status="accepted" if status == "received" else "pending",
        ))

    # ---- Production orders (last 14 days) ----
    prod_specs = [
        (pl_pkg, "PST-001", 500, "completed", 12),
        (pl_pkg, "PST-002", 300, "completed", 10),
        (pl_asm, "PST-005", 800, "in_progress", 4),
        (pl_prc, "SEM-002", 400, "planned", 2),
        (pl_pkg, "PST-003", 4000, "completed", 6),
        (pl_asm, "PST-006", 350, "planned", 1),
    ]
    for i, (line, sku, qty, status, days) in enumerate(prod_specs, start=1):
        prod = by_sku[sku]
        produced = round(qty * 0.9) if status == "completed" else (round(qty * 0.5) if status == "in_progress" else 0)
        db.add(ProductionOrder(
            factory_id=fid, line_id=line.id, product_id=prod.id,
            order_number=f"PRD-2026{str(i).zfill(4)}", planned_qty=qty, produced_qty=produced,
            scrap_qty=round(qty * 0.02), status=status,
            planned_start=_days_ago(days), planned_end=_days_ago(max(0, days - 1)),
            actual_start=_days_ago(days) if status != "planned" else None,
            priority=3,
        ))

    # ---- Quality checks ----
    qc_specs = [
        ("ipqc", "PST-001", 50, 2, "passed"),
        ("iqc", "RM-003", 100, 0, "passed"),
        ("oqc", "PST-003", 80, 9, "failed"),
        ("ipqc", "PST-005", 60, 3, "passed"),
        ("oqc", "PST-002", 40, 1, "passed"),
    ]
    failed_qc = None
    for check_type, sku, sample, defects, status in qc_specs:
        prod = by_sku.get(sku)
        rate = round(defects / sample * 100, 2) if sample else 0
        qc = QualityCheck(
            factory_id=fid, check_type=check_type, product_id=prod.id if prod else None,
            status=status, checked_at=_days_ago(random.randint(1, 8)), sample_size=sample,
            defects_found=defects, defect_rate_pct=rate,
            decision="accept" if status == "passed" else "reject",
        )
        db.add(qc)
        db.flush()
        if status == "failed":
            failed_qc = qc

    # ---- NCR + CAPA ----
    if failed_qc:
        ncr = NonConformanceReport(
            factory_id=fid, ncr_number="NCR-2026-001", title="OQC failure on Bottled Drink 500ml",
            description="Defect rate 11.25% exceeded 5% limit on cap seal.", severity="major",
            status="open", quality_check_id=failed_qc.id, root_cause="Cap torque mis-set on filler.",
            opened_at=_days_ago(6),
        )
        db.add(ncr)
        db.flush()
        db.add(CAPARecord(
            factory_id=fid, capa_number="CAPA-2026-001", type="corrective", ncr_id=ncr.id,
            description="Recalibrate cap torque on PRC-03 and add in-line vision check.",
            responsible_person="Maintenance Lead", due_date=_days_ahead(7), status="open",
        ))

    # ---- Maintenance ----
    # schedule for a couple machines
    db.add(MaintenanceSchedule(factory_id=fid, machine_id=machines[0].id, type="preventive",
                               frequency_days=90, last_done=_days_ago(30),
                               next_due=_days_ahead(60), active=True))
    db.add(MaintenanceSchedule(factory_id=fid, machine_id=machines[4].id, type="predictive",
                               frequency_days=60, last_done=_days_ago(70),
                               next_due=_days_ago(10), active=True))  # overdue
    db.add(MaintenanceWorkOrder(
        factory_id=fid, machine_id=machines[4].id, wo_number="WO-2026-001", type="preventive",
        status="completed", priority="medium", description="Quarterly calibration.",
        assigned_to="Tech A", created_at=_days_ago(40), started_at=_days_ago(40),
        completed_at=_days_ago(39), downtime_hours=4, resolution="Calibrated.",
    ))
    db.add(MaintenanceWorkOrder(
        factory_id=fid, machine_id=machines[5].id, wo_number="WO-2026-002", type="corrective",
        status="in_progress", priority="high", description="Reactor overheating.",
        assigned_to="Tech B", created_at=_days_ago(2), started_at=_days_ago(1),
        downtime_hours=6,
    ))
    db.add(MachineBreakdown(
        factory_id=fid, machine_id=machines[7].id, occurred_at=_days_ago(3),
        resolved_at=_days_ago(2), cause_category="electrical",
        description="Compressor motor failure.", impact_on_production="Low — utility backup used.",
    ))

    # ---- Workforce + attendance ----
    depts = ["Production", "Quality", "Maintenance", "Logistics", "Supervision"]
    workers = []
    for i in range(1, 11):
        w = Worker(
            factory_id=fid, employee_id=f"EMP-{str(i).zfill(3)}", name=f"Worker {i}",
            department=depts[i % len(depts)], role="Operator",
            skills="packing;quality" if i % 2 else "assembly;forklift", status="active",
        )
        db.add(w)
        db.flush()
        workers.append(w)
        for d in range(7):
            day = _today() - dt.timedelta(days=d)
            if day.weekday() >= 5:
                continue
            status = "present" if random.random() > 0.08 else ("late" if random.random() > 0.5 else "absent")
            db.add(AttendanceRecord(
                factory_id=fid, worker_id=w.id, record_date=day, scheduled=True,
                status=status, overtime_hours=round(random.uniform(0, 2), 1) if status == "present" else 0,
            ))
        # shift assignment for this week
        db.add(ShiftAssignment(
            factory_id=fid, worker_id=w.id, shift_id=shifts[0].id,
            week_start=_today() - dt.timedelta(days=_today().weekday()),
            day_of_week=(i % 5) + 1,
        ))

    # ---- Product costs (last 3 months) ----
    months = [(_today().replace(day=1) - dt.timedelta(days=32 * k)).strftime("%Y-%m") for k in range(3)]
    months = sorted(set(months))
    for p in products[:6]:
        for mi, mlabel in enumerate(months):
            std = p.standard_cost
            act = round(std * random.uniform(0.95, 1.12), 2)
            db.add(ProductCost(
                factory_id=fid, product_id=p.id, period_label=mlabel,
                std_material_cost=std, act_material_cost=act,
                std_labor_cost=round(std * 0.3, 2), act_labor_cost=round(std * 0.3 * random.uniform(0.9, 1.1), 2),
                std_overhead_cost=round(std * 0.2, 2), act_overhead_cost=round(std * 0.2 * random.uniform(0.9, 1.1), 2),
                std_total=round(std * 1.5, 2), act_total=round(act * 1.5, 2),
            ))

    # ---- KPI definitions ----
    kpi_defs = [
        ("plan_adherence", "Plan Adherence", "production", 95, 90, 80, True, "percentage"),
        ("oee", "OEE", "production", 85, 75, 65, True, "percentage"),
        ("machine_availability", "Machine Availability", "production", 90, 80, 70, True, "percentage"),
        ("otif", "OTIF %", "sales", 95, 90, 80, True, "percentage"),
        ("order_fill_rate", "Order Fill Rate", "sales", 98, 92, 85, True, "percentage"),
        ("inventory_days", "Inventory Days of Cover", "inventory", 30, 45, 60, False, "number"),
        ("inventory_health", "Inventory Health", "inventory", 90, 75, 60, True, "percentage"),
        ("quality_fpy", "Quality FPY", "quality", 98, 95, 90, True, "percentage"),
        ("defect_rate", "Defect Rate", "quality", 2, 5, 8, False, "percentage"),
        ("pm_compliance", "PM Compliance", "maintenance", 95, 85, 75, True, "percentage"),
        ("mtbf", "MTBF (hours)", "maintenance", 720, 500, 300, True, "number"),
        ("gross_margin", "Gross Margin", "financial", 35, 25, 15, True, "percentage"),
        ("cost_variance", "Cost Variance", "financial", 3, 8, 12, False, "percentage"),
    ]
    kpi_objs = []
    for code, name, cat, target, warn, crit, hib, fmt in kpi_defs:
        kd = KPIDefinition(
            factory_id=fid, code=code, name=name, category=cat, target_value=target,
            warning_threshold=warn, critical_threshold=crit, higher_is_better=hib,
            display_format=fmt, is_custom=False, is_active=True,
        )
        db.add(kd)
        db.flush()
        kpi_objs.append(kd)

    # KPI values last 30 days
    for kd in kpi_objs:
        base = kd.target_value or 50
        for d in range(30, 0, -1):
            day = _days_ago(d)
            noise = random.uniform(-0.06, 0.06)
            trend = (30 - d) / 600.0  # slight upward
            val = base * (1 + noise + trend)
            if kd.higher_is_better:
                val = max(val, kd.critical_threshold * 0.9)
            else:
                val = min(val, kd.critical_threshold * 1.2)
            status = "good"
            if kd.higher_is_better:
                if val < (kd.critical_threshold or 0): status = "critical"
                elif val < (kd.warning_threshold or 0): status = "warning"
            else:
                if val > (kd.critical_threshold or 100): status = "critical"
                elif val > (kd.warning_threshold or 100): status = "warning"
            db.add(KPIValue(
                kpi_id=kd.id, factory_id=fid, period_type="daily", period_date=day,
                value=round(val, 2), status=status, calculated_at=_now(),
            ))

    # ---- Alerts ----
    alerts = [
        ("stockout", "emergency", "Raw material CAP (RM-015) stock at ZERO",
         "Cap inventory reached 0 — packaging line at risk of stoppage.", "inventory", by_rm["RM-015"].id),
        ("low_stock", "critical", "Cocoa Powder below safety stock",
         "On hand 40 vs safety 100 — reorder immediately.", "inventory", by_rm["RM-007"].id),
        ("quality", "critical", "OQC failure — Bottled Drink 500ml",
         "Defect rate 11.25% exceeds limit. CAPA opened.", "quality", failed_qc.id if failed_qc else None),
        ("maintenance", "warning", "Preventive maintenance overdue — Mixer",
         "Next due 10 days ago. Schedule corrective window.", "maintenance", machines[4].id),
        ("delivery", "warning", "Purchase order PO-2026-002 overdue",
         "Expected 2 days ago, still in transit.", "procurement", None),
        ("info", "info", "Daily production plan generated",
         "6 orders scheduled across 3 lines.", "production", None),
    ]
    for atype, sev, title, msg, mod, sid in alerts:
        db.add(Alert(
            factory_id=fid, alert_type=atype, severity=sev, title=title, message=msg,
            source_module=mod, source_id=sid, is_read=(sev == "info"), is_resolved=False,
            created_at=_days_ago(random.randint(0, 3)),
        ))

    # ---- Decisions ----
    decisions = [
        ("procurement", "Approve urgent PO for Cocoa Powder",
         "RM-007 critically low. Issue PO-2026-004 to NutFarm.",
         "Cost EGP 300; avoids line stoppage.", "urgent"),
        ("production", "Reschedule PST-006 to Night shift",
         "Assembly line overloaded in afternoon; move 350 units to Night.",
         "Improves adherence to 96%.", "high"),
        ("sales", "Accept rush order CUST-004",
         "400 units PST-006 due in 1 day. Capacity available on Night shift.",
         "Revenue EGP 2,200; margin positive.", "high"),
    ]
    for dtype, title, desc, rec, prio in decisions:
        db.add(Decision(
            factory_id=fid, decision_type=dtype, title=title, description=desc,
            recommendation=rec, impact_summary={}, status="pending", priority=prio,
            created_at=_days_ago(1),
        ))

    # ---- Demand forecasts (last 6 + next 3 months) ----
    for p in products[:5]:
        for k in range(-6, 3):
            mlabel = (_today().replace(day=1) + dt.timedelta(days=32 * k)).strftime("%Y-%m")
            hist = random.randint(500, 2000) if k < 0 else 0
            sys_f = random.randint(600, 1800)
            db.add(DemandForecast(
                factory_id=fid, product_id=p.id, period_type="monthly", period_label=mlabel,
                historical=hist, system_forecast=sys_f, final_forecast=sys_f,
            ))

    # ---- App settings ----
    defaults = {
        "language": "en",
        "default_factory_id": str(fid),
        "auto_backup": "true",
        "auto_backup_time": "23:00",
        "backup_keep": "30",
        "theme": "light",
    }
    for k, v in defaults.items():
        db.add(AppSetting(key=k, value=v, description=""))

    db.add(BackupLog(
        filename="emicp_seed.db", backup_type="manual", file_size_bytes=0,
        file_path="seed", status="success", created_at=_now(),
    ))

    db.commit()
