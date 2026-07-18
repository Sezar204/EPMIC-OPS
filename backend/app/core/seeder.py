Input
"""Seed demo data for a brand-new EMICP install."""
import logging
import random
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import (
    Factory, ProductionLine, Machine, Shift, Product, BOMHeader, BOMLine,
    RawMaterial, InventoryRawMaterial, InventoryFinishedGoods,
    Customer, SalesOrder, SalesOrderLine,
    Supplier, SupplierMaterial, PurchaseOrder, PurchaseOrderLine,
    Warehouse, QualityCheck, NonConformanceReport, CAPARecord,
    MaintenanceWorkOrder, Worker, AttendanceRecord, ProductCost,
    KPIDefinition, KPIValue, Alert, Decision, AppSetting,
)

logger = logging.getLogger(__name__)


def _has_data(db: Session) -> bool:
    return db.execute(select(Factory).limit(1)).first() is not None


def seed_demo_data(db: Session) -> dict:
    """Populate a realistic demo dataset. Idempotent: skips if data exists."""
    if _has_data(db):
        return {"seeded": False, "reason": "already has data"}

    rng = random.Random(42)
    today = date.today()

    # ---------- Factory ----------
    factory = Factory(
        code="CAI-01", name="Cairo Manufacturing Plant",
        type="hybrid", status="active", location="Cairo, Egypt",
        currency="EGP", timezone="Africa/Cairo",
        working_start="08:00", working_end="17:00",
        notes="Main demo factory — packaged goods production.",
    )
    db.add(factory); db.flush()
    fid = factory.id

    # ---------- Production Lines ----------
    lines = [
        ProductionLine(factory_id=fid, code="PKG-01", name="Packaging Line A",
                       type="discrete", capacity_per_hour=500, capacity_unit="pcs",
                       status="active", changeover_minutes=20),
        ProductionLine(factory_id=fid, code="ASM-01", name="Assembly Line B",
                       type="discrete", capacity_per_hour=200, capacity_unit="pcs",
                       status="active", changeover_minutes=30),
        ProductionLine(factory_id=fid, code="PRC-01", name="Processing Line C",
                       type="process", capacity_per_hour=1000, capacity_unit="kg",
                       status="idle",   changeover_minutes=45),
    ]
    db.add_all(lines); db.flush()

    # ---------- Machines ----------
    machines = [
        Machine(factory_id=fid, line_id=lines[0].id, code="M-101", name="Filler A1",
                type="filler", capacity=600, capacity_unit="pcs/h",
                criticality="high", status="active"),
        Machine(factory_id=fid, line_id=lines[0].id, code="M-102", name="Capper A2",
                type="capper", capacity=600, capacity_unit="pcs/h",
                criticality="high", status="active"),
        Machine(factory_id=fid, line_id=lines[1].id, code="M-201", name="Conveyor B1",
                type="conveyor", capacity=300, capacity_unit="pcs/h",
                criticality="medium", status="active"),
        Machine(factory_id=fid, line_id=lines[1].id, code="M-202", name="Labeler B2",
                type="labeler", capacity=250, capacity_unit="pcs/h",
                criticality="medium", status="maintenance"),
        Machine(factory_id=fid, line_id=lines[2].id, code="M-301", name="Mixer C1",
                type="mixer", capacity=1200, capacity_unit="kg/h",
                criticality="critical", status="active"),
        Machine(factory_id=fid, line_id=lines[2].id, code="M-302", name="Reactor C2",
                type="reactor", capacity=800, capacity_unit="kg/h",
                criticality="critical", status="down"),
        Machine(factory_id=fid, code="M-401", name="Boiler D1",
                type="boiler", capacity=2000, capacity_unit="kg/h",
                criticality="high", status="active"),
        Machine(factory_id=fid, code="M-402", name="Compressor D2",
                type="compressor", capacity=1500, capacity_unit="kg/h",
                criticality="medium", status="active"),
    ]
    db.add_all(machines); db.flush()

    # ---------- Shifts ----------
    shifts = [
        Shift(factory_id=fid, name="Morning",   start_time="06:00", end_time="14:00",
              break_minutes=30, days_of_week="1,2,3,4,5", headcount=8, is_active=True),
        Shift(factory_id=fid, name="Afternoon", start_time="14:00", end_time="22:00",
              break_minutes=30, days_of_week="1,2,3,4,5", headcount=8, is_active=True),
        Shift(factory_id=fid, name="Night",     start_time="22:00", end_time="06:00",
              break_minutes=45, days_of_week="1,2,3,4,5,6,7", headcount=5, is_active=True),
    ]
    db.add_all(shifts); db.flush()

    # ---------- Products ----------
    products = [
        Product(factory_id=fid, sku="BTL-500",  name="Bottle 500ml",     category="Beverage", unit_of_measure="pcs",
                standard_cost=0.50, selling_price=1.25, min_order_qty=500,  lead_time_days=3, type="finished"),
        Product(factory_id=fid, sku="BTL-1L",   name="Bottle 1L",        category="Beverage", unit_of_measure="pcs",
                standard_cost=0.85, selling_price=2.00, min_order_qty=300,  lead_time_days=3, type="finished"),
        Product(factory_id=fid, sku="CAP-28",   name="Cap 28mm",         category="Packaging", unit_of_measure="pcs",
                standard_cost=0.05, selling_price=0.12, min_order_qty=1000, lead_time_days=2, type="semi-finished"),
        Product(factory_id=fid, sku="LBL-FR",   name="Front Label",      category="Packaging", unit_of_measure="pcs",
                standard_cost=0.02, selling_price=0.06, min_order_qty=2000, lead_time_days=4, type="semi-finished"),
        Product(factory_id=fid, sku="JUICE-OR", name="Orange Juice 1L",  category="Beverage", unit_of_measure="pcs",
                standard_cost=1.10, selling_price=2.80, min_order_qty=200,  lead_time_days=4, shelf_life_days=180, type="finished"),
        Product(factory_id=fid, sku="JUICE-AP", name="Apple Juice 1L",   category="Beverage", unit_of_measure="pcs",
                standard_cost=1.15, selling_price=2.90, min_order_qty=200,  lead_time_days=4, shelf_life_days=180, type="finished"),
        Product(factory_id=fid, sku="WATER-500",name="Mineral Water 500",category="Beverage", unit_of_measure="pcs",
                standard_cost=0.20, selling_price=0.75, min_order_qty=1000, lead_time_days=2, type="finished"),
        Product(factory_id=fid, sku="SYRUP",    name="Fruit Syrup Base", category="Ingredient", unit_of_measure="kg",
                standard_cost=2.30, selling_price=0,    min_order_qty=50,   lead_time_days=5, type="semi-finished"),
        Product(factory_id=fid, sku="BOX-12",   name="Box of 12",        category="Packaging", unit_of_measure="pcs",
                standard_cost=0.30, selling_price=0,    min_order_qty=300,  lead_time_days=5, type="finished"),
        Product(factory_id=fid, sku="PROMO-3",  name="3-Bottle Pack",    category="Beverage", unit_of_measure="pcs",
                standard_cost=1.40, selling_price=3.50, min_order_qty=200,  lead_time_days=3, type="finished"),
    ]
    db.add_all(products); db.flush()

    # ---------- Raw Materials ----------
    raw_materials = [
        RawMaterial(factory_id=fid, code="RM-PET",   name="PET Resin",       category="Plastic",     unit_of_measure="kg",
                    standard_cost=1.50, safety_stock_qty=500, reorder_point_qty=1000, lead_time_days=10, storage_conditions="dry"),
        RawMaterial(factory_id=fid, code="RM-HDPE",  name="HDPE Resin",      category="Plastic",     unit_of_measure="kg",
                    standard_cost=1.65, safety_stock_qty=400, reorder_point_qty=800,  lead_time_days=10, storage_conditions="dry"),
        RawMaterial(factory_id=fid, code="RM-PAPER", name="Label Paper",     category="Paper",       unit_of_measure="roll",
                    standard_cost=12.0, safety_stock_qty=20,  reorder_point_qty=40,   lead_time_days=5,  storage_conditions="dry"),
        RawMaterial(factory_id=fid, code="RM-INK",   name="Printing Ink",    category="Chemical",    unit_of_measure="liter",
                    standard_cost=8.0,  safety_stock_qty=30,  reorder_point_qty=60,   lead_time_days=7,  storage_conditions="cool"),
        RawMaterial(factory_id=fid, code="RM-ORJUICE",name="Orange Concentrate", category="Ingredient", unit_of_measure="liter",
                    standard_cost=3.20, safety_stock_qty=200, reorder_point_qty=400,  lead_time_days=5,  shelf_life_days=120, storage_conditions="cold"),
        RawMaterial(factory_id=fid, code="RM-APJUICE",name="Apple Concentrate",  category="Ingredient", unit_of_measure="liter",
                    standard_cost=3.10, safety_stock_qty=200, reorder_point_qty=400,  lead_time_days=5,  shelf_life_days=120, storage_conditions="cold"),
        RawMaterial(factory_id=fid, code="RM-SUGAR", name="Sugar",           category="Ingredient",  unit_of_measure="kg",
                    standard_cost=0.80, safety_stock_qty=500, reorder_point_qty=1000, lead_time_days=3),
        RawMaterial(factory_id=fid, code="RM-WATER", name="RO Water",        category="Ingredient",  unit_of_measure="liter",
                    standard_cost=0.05, safety_stock_qty=2000,reorder_point_qty=5000, lead_time_days=1),
        RawMaterial(factory_id=fid, code="RM-CA",    name="Citric Acid",     category="Chemical",    unit_of_measure="kg",
                    standard_cost=2.10, safety_stock_qty=50,  reorder_point_qty=100,  lead_time_days=7),
        RawMaterial(factory_id=fid, code="RM-VITC",  name="Vitamin C",       category="Chemical",    unit_of_measure="kg",
                    standard_cost=12.5, safety_stock_qty=10,  reorder_point_qty=20,   lead_time_days=14, shelf_life_days=365),
        RawMaterial(factory_id=fid, code="RM-CAP",   name="Cap Resin",       category="Plastic",     unit_of_measure="kg",
                    standard_cost=1.85, safety_stock_qty=200, reorder_point_qty=400,  lead_time_days=10),
        RawMaterial(factory_id=fid, code="RM-BOX",   name="Cardboard Sheet", category="Paper",       unit_of_measure="pcs",
                    standard_cost=0.30, safety_stock_qty=500, reorder_point_qty=1000, lead_time_days=5),
        RawMaterial(factory_id=fid, code="RM-FLAV",  name="Flavor Mix",      category="Ingredient",  unit_of_measure="kg",
                    standard_cost=18.0, safety_stock_qty=10,  reorder_point_qty=20,   lead_time_days=10, shelf_life_days=240),
        RawMaterial(factory_id=fid, code="RM-COLOR", name="Colorant",        category="Chemical",    unit_of_measure="kg",
                    standard_cost=5.5,  safety_stock_qty=20,  reorder_point_qty=40,   lead_time_days=7),
        RawMaterial(factory_id=fid, code="RM-SALT",  name="Salt",            category="Ingredient",  unit_of_measure="kg",
                    standard_cost=0.30, safety_stock_qty=100, reorder_point_qty=200,  lead_time_days=3),
    ]
    db.add_all(raw_materials); db.flush()

    # ---------- BOMs ----------
    def add_bom(product, lines_data):
        bom = BOMHeader(factory_id=fid, product_id=product.id, version="1.0",
                        name=f"BOM {product.sku} v1.0", status="active", yield_pct=98)
        db.add(bom); db.flush()
        for seq, (mat_idx, qty, unit) in enumerate(lines_data, 1):
            db.add(BOMLine(bom_id=bom.id, material_id=raw_materials[mat_idx].id,
                           quantity_required=qty, unit=unit, sequence_no=seq))
        return bom

    add_bom(products[0], [(0, 0.025, "kg"), (2, 0.001, "roll"), (3, 0.0002, "liter"), (10, 0.005, "kg")])
    add_bom(products[1], [(1, 0.040, "kg"), (2, 0.001, "roll"), (3, 0.0002, "liter"), (10, 0.005, "kg")])
    add_bom(products[2], [(0, 0.003, "kg")])
    add_bom(products[3], [(2, 0.001, "roll"), (3, 0.0001, "liter")])
    add_bom(products[4], [(4, 0.20, "liter"), (6, 0.05, "kg"), (7, 0.70, "liter"),
                         (8, 0.002, "kg"), (9, 0.0005, "kg"), (12, 0.005, "kg")])
    add_bom(products[5], [(5, 0.20, "liter"), (6, 0.05, "kg"), (7, 0.70, "liter"),
                         (8, 0.002, "kg"), (9, 0.0005, "kg")])
    add_bom(products[6], [(7, 0.50, "liter"), (14, 0.001, "kg")])
    add_bom(products[7], [(6, 0.65, "kg"), (7, 0.30, "liter"), (8, 0.005, "kg"),
                         (12, 0.010, "kg"), (13, 0.002, "kg")])
    add_bom(products[8], [(11, 1.0, "pcs"), (2, 0.05, "roll")])
    add_bom(products[9], [(0, 0.075, "kg"), (1, 0.040, "kg"), (2, 0.003, "roll"),
                         (3, 0.0006, "liter"), (10, 0.015, "kg")])

    # ---------- Suppliers ----------
    suppliers = [
        Supplier(factory_id=fid, code="SUP-PET",  name="Egyptian Petrochem Co.",   rating=5, status="active", payment_terms_days=30),
        Supplier(factory_id=fid, code="SUP-PAP",  name="Nile Paper Mills",         rating=4, status="active", payment_terms_days=45),
        Supplier(factory_id=fid, code="SUP-ING",  name="Agro Ingredients Ltd",     rating=4, status="active", payment_terms_days=30),
        Supplier(factory_id=fid, code="SUP-CHEM", name="ChemSource International", rating=3, status="active", payment_terms_days=60),
        Supplier(factory_id=fid, code="SUP-BOX",  name="Cairo Packaging Group",    rating=5, status="active", payment_terms_days=30),
    ]
    db.add_all(suppliers); db.flush()
    db.add_all([
        SupplierMaterial(supplier_id=suppliers[0].id, material_id=raw_materials[0].id, supplier_price=1.45, lead_time_days=10, is_preferred=True),
        SupplierMaterial(supplier_id=suppliers[0].id, material_id=raw_materials[1].id, supplier_price=1.60, lead_time_days=10, is_preferred=True),
        SupplierMaterial(supplier_id=suppliers[1].id, material_id=raw_materials[2].id, supplier_price=11.5, lead_time_days=5,  is_preferred=True),
        SupplierMaterial(supplier_id=suppliers[2].id, material_id=raw_materials[4].id, supplier_price=3.10, lead_time_days=5,  is_preferred=True),
        SupplierMaterial(supplier_id=suppliers[2].id, material_id=raw_materials[5].id, supplier_price=3.00, lead_time_days=5,  is_preferred=True),
        SupplierMaterial(supplier_id=suppliers[3].id, material_id=raw_materials[3].id, supplier_price=7.8,  lead_time_days=7,  is_preferred=True),
        SupplierMaterial(supplier_id=suppliers[3].id, material_id=raw_materials[8].id, supplier_price=2.05, lead_time_days=7,  is_preferred=True),
        SupplierMaterial(supplier_id=suppliers[4].id, material_id=raw_materials[11].id, supplier_price=0.28, lead_time_days=5,  is_preferred=True),
    ])

    # ---------- Customers ----------
    customers = [
        Customer(factory_id=fid, code="CUST-HM",  name="Hypermarket Co",         type="b2b",          priority=1, credit_limit=500000, payment_terms_days=60),
        Customer(factory_id=fid, code="CUST-SUP", name="SuperStore Chain",       type="b2b",          priority=2, credit_limit=300000, payment_terms_days=45),
        Customer(factory_id=fid, code="CUST-DIS", name="Regional Distributor",   type="distributor",  priority=1, credit_limit=800000, payment_terms_days=30),
        Customer(factory_id=fid, code="CUST-CAF", name="Cafe Network",           type="b2b",          priority=3, credit_limit=50000,  payment_terms_days=30),
        Customer(factory_id=fid, code="CUST-EXP", name="Export Trading Co",      type="b2b",          priority=2, credit_limit=200000, payment_terms_days=90),
    ]
    db.add_all(customers); db.flush()

    # ---------- Warehouse ----------
    warehouse = Warehouse(factory_id=fid, code="WH-MAIN", name="Main Warehouse",
                          type="general", total_capacity=5000, capacity_unit="sqm",
                          storage_conditions="ambient", location="Cairo")
    db.add(warehouse); db.flush()
    wh_id = warehouse.id

    # ---------- Inventory (raw + finished) ----------
    # 3 below safety, 1 zero
    inv_raw_levels = [1200, 200, 60, 35, 800, 350, 1500, 6500, 80, 25, 600, 1100, 8, 18, 0]
    for mat, lvl in zip(raw_materials, inv_raw_levels):
        db.add(InventoryRawMaterial(
            factory_id=fid, material_id=mat.id, warehouse_id=wh_id,
            qty_on_hand=lvl, qty_reserved=0, qty_available=lvl,
            last_movement_date=today - timedelta(days=rng.randint(0, 30)),
        ))
    for prod in products[:7]:
        db.add(InventoryFinishedGoods(
            factory_id=fid, product_id=prod.id, warehouse_id=wh_id,
            qty_on_hand=rng.randint(100, 1500),
            qty_reserved=0, qty_available=rng.randint(100, 1500),
            last_updated=datetime.utcnow(),
        ))

    # ---------- Sales Orders ----------
    so_statuses = ["draft", "confirmed", "in_production", "ready", "shipped", "delivered"]
    for i in range(5):
        cust = customers[i % len(customers)]
        so = SalesOrder(
            factory_id=fid, customer_id=cust.id,
            order_number=f"ORD-{today.strftime('%Y%m%d')}-{i+1:03d}",
            order_date=today - timedelta(days=rng.randint(0, 30)),
            required_delivery=today + timedelta(days=rng.randint(-5, 21)),
            status=rng.choice(so_statuses),
            total_value=rng.randint(5000, 80000),
            currency=factory.currency,
            is_rush_order=(i == 0),
            priority=rng.randint(1, 5),
        )
        db.add(so); db.flush()
        for j in range(rng.randint(1, 3)):
            prod = rng.choice(products[:7])
            qty  = rng.randint(50, 500)
            price = prod.selling_price
            db.add(SalesOrderLine(
                order_id=so.id, product_id=prod.id,
                quantity=qty, unit_price=price, discount_pct=0,
                line_total=qty * price, status="open",
            ))

    # ---------- Purchase Orders ----------
    po_statuses = ["planned", "issued", "in_transit", "received", "closed"]
    for i in range(3):
        sup = suppliers[i % len(suppliers)]
        expected = today + timedelta(days=[-3, 5, 10][i])
        po = PurchaseOrder(
            factory_id=fid, supplier_id=sup.id,
            po_number=f"PO-{today.strftime('%Y%m%d')}-{i+1:03d}",
            order_date=today - timedelta(days=rng.randint(5, 20)),
            expected_delivery=expected,
            status=po_statuses[i],
            total_value=rng.randint(2000, 25000),
            currency=factory.currency,
        )
        db.add(po); db.flush()
        for j in range(rng.randint(1, 2)):
            mat = rng.choice(raw_materials)
            qty = rng.randint(50, 300)
            db.add(PurchaseOrderLine(
                po_id=po.id, material_id=mat.id,
                qty_ordered=qty, unit_price=mat.standard_cost,
                qty_received=qty if i == 2 else 0,
                quality_status="accepted" if i == 2 else "pending",
            ))

    # ---------- Quality ----------
    db.add_all([
        QualityCheck(factory_id=fid, check_type="iqc", product_id=products[0].id,
                     status="passed", sample_size=50, defects_found=0,
                     defect_rate_pct=0, decision="accept",
                     checked_at=datetime.utcnow() - timedelta(days=2)),
        QualityCheck(factory_id=fid, check_type="ipqc", product_id=products[4].id,
                     status="passed", sample_size=30, defects_found=1,
                     defect_rate_pct=3.3, decision="accept",
                     checked_at=datetime.utcnow() - timedelta(days=1)),
        QualityCheck(factory_id=fid, check_type="oqc", product_id=products[5].id,
                     status="failed", sample_size=40, defects_found=5,
                     defect_rate_pct=12.5, decision="reject",
                     checked_at=datetime.utcnow() - timedelta(hours=8)),
        QualityCheck(factory_id=fid, check_type="iqc", material_id=raw_materials[0].id,
                     status="passed", sample_size=10, defects_found=0,
                     defect_rate_pct=0, decision="accept",
                     checked_at=datetime.utcnow() - timedelta(days=5)),
        QualityCheck(factory_id=fid, check_type="oqc", product_id=products[6].id,
                     status="passed", sample_size=60, defects_found=1,
                     defect_rate_pct=1.7, decision="accept",
                     checked_at=datetime.utcnow() - timedelta(hours=2)),
    ])

    # ---------- NCR + CAPA ----------
    ncr = NonConformanceReport(
        factory_id=fid, ncr_number=f"NCR-{today.strftime('%Y%m%d')}-001",
        title="Apple Juice batch failed OQC — high defect rate",
        description="5 defects in 40 sample units; bottle seal failure.",
        severity="high", status="open", root_cause="",
    )
    db.add(ncr); db.flush()
    db.add(CAPARecord(
        factory_id=fid, capa_number=f"CAPA-{today.strftime('%Y%m%d')}-001",
        type="corrective", ncr_id=ncr.id,
        description="Inspect capper torque settings; replace worn seal rings; re-validate.",
        responsible_person="Maintenance Lead",
        due_date=datetime.utcnow() + timedelta(days=14),
        status="open",
    ))

    # ---------- Maintenance Work Orders ----------
    db.add_all([
        MaintenanceWorkOrder(factory_id=fid, machine_id=machines[3].id,
                             wo_number="WO-001", type="corrective",
                             status="in_progress", priority="high",
                             description="Labeler B2 not applying labels consistently.",
                             assigned_to="Ahmed M.", started_at=datetime.utcnow() - timedelta(hours=4),
                             downtime_hours=4),
        MaintenanceWorkOrder(factory_id=fid, machine_id=machines[1].id,
                             wo_number="WO-002", type="preventive",
                             status="completed", priority="medium",
                             description="Quarterly PM — capper calibration.",
                             assigned_to="Sara K.", started_at=datetime.utcnow() - timedelta(days=3),
                             completed_at=datetime.utcnow() - timedelta(days=3, hours=-2),
                             downtime_hours=2, resolution="Replaced O-ring; calibrated torque."),
    ])

    # ---------- Workers + Attendance ----------
    worker_names = [
        ("E-001", "Ahmed Hassan",   "Production", "Operator"),
        ("E-002", "Sara Mahmoud",   "Production", "Operator"),
        ("E-003", "Mohamed Ali",    "Production", "Line Lead"),
        ("E-004", "Fatma Said",     "Quality",    "Inspector"),
        ("E-005", "Karim Nabil",    "Quality",    "Inspector"),
        ("E-006", "Yasmin Adel",    "Maintenance","Technician"),
        ("E-007", "Omar Tarek",     "Warehouse",  "Forklift"),
        ("E-008", "Hala Mostafa",   "Production", "Operator"),
        ("E-009", "Tamer Gamal",    "Production", "Operator"),
        ("E-010", "Nour Eldin",     "Maintenance","Technician"),
    ]
    workers = []
    for emp_id, name, dept, role in worker_names:
        w = Worker(factory_id=fid, employee_id=emp_id, name=name,
                   department=dept, role=role, status="active",
                   skills=[role, dept])
        workers.append(w)
        db.add(w)
    db.flush()
    # 7 days of attendance
    for w in workers:
        for d in range(7):
            att_date = today - timedelta(days=d)
            status = "present" if rng.random() > 0.08 else ("absent" if rng.random() > 0.5 else "late")
            db.add(AttendanceRecord(
                factory_id=fid, worker_id=w.id, attendance_date=att_date,
                scheduled_hours=8, actual_hours=8 if status == "present" else (7 if status == "late" else 0),
                ot_hours=rng.choice([0, 0, 0, 1, 2]),
                status=status,
            ))

    # ---------- Product Costs (3 months) ----------
    for prod in products[:7]:
        for m in range(3):
            period = (today.replace(day=1) - timedelta(days=30 * m))
            std = prod.standard_cost
            variance = rng.uniform(0.92, 1.12)
            db.add(ProductCost(
                factory_id=fid, product_id=prod.id, period_date=period,
                std_material_cost=std * 0.55, act_material_cost=std * 0.55 * variance,
                std_labor_cost=std * 0.25,    act_labor_cost=std * 0.25 * variance,
                std_overhead_cost=std * 0.20, act_overhead_cost=std * 0.20 * variance,
                std_total_cost=std,           act_total_cost=std * variance,
                revenue=prod.selling_price * rng.randint(500, 2000),
            ))

    # ---------- KPI Definitions ----------
    kpi_defs = [
        ("OEE",          "OEE %",             "production",   "%",  85, 75, 60,  True,  "percentage"),
        ("PLAN_ADH",     "Plan Adherence",    "production",   "%",  95, 85, 70,  True,  "percentage"),
        ("OTIF",         "OTIF %",            "sales",        "%",  95, 85, 75,  True,  "percentage"),
        ("INV_DAYS",     "Inventory Days",    "inventory",    "d",  30, 45, 60,  False, "number"),
        ("QUALITY_FPY",  "First Pass Yield",  "quality",      "%",  98, 95, 90,  True,  "percentage"),
        ("DEFECT_RATE",  "Defect Rate",       "quality",      "%",  2,  4,  6,   False, "percentage"),
        ("PM_COMPL",     "PM Compliance",     "maintenance",  "%",  95, 85, 70,  True,  "percentage"),
        ("AVAIL",        "Machine Availability","maintenance","%",  90, 80, 70,  True,  "percentage"),
        ("ATTEND",       "Attendance Rate",   "financial",    "%",  95, 90, 85,  True,  "percentage"),
        ("MARGIN",       "Gross Margin",      "financial",    "%",  35, 25, 15,  True,  "percentage"),
    ]
    kpi_rows = []
    for code, name, cat, unit, tgt, warn, crit, hib, fmt in kpi_defs:
        kpi_rows.append(KPIDefinition(
            factory_id=fid, code=code, name=name, category=cat, unit=unit,
            target_value=tgt, warning_threshold=warn, critical_threshold=crit,
            higher_is_better=hib, display_format=fmt, is_custom=False, is_active=True,
        ))
    db.add_all(kpi_rows); db.flush()

    # 30 days of KPI values for sparklines
    for kpi in kpi_rows:
        for d in range(30):
            dt = today - timedelta(days=d)
            tgt = kpi.target_value or 80
            val = tgt + rng.uniform(-10, 10)
            if kpi.higher_is_better:
                val = max(0, min(100, val))
            else:
                val = max(0, val)
            status = "good"
            if kpi.higher_is_better:
                if val < (kpi.critical_threshold or 0): status = "critical"
                elif val < (kpi.warning_threshold or 0): status = "warning"
            else:
                if val > (kpi.critical_threshold or 100): status = "critical"
                elif val > (kpi.warning_threshold or 100): status = "warning"
            db.add(KPIValue(
                kpi_id=kpi.id, factory_id=fid,
                period_type="daily", period_date=dt,
                value=round(val, 2), status=status,
                calculated_at=datetime.utcnow(),
            ))

    # ---------- Alerts ----------
    db.add_all([
        Alert(factory_id=fid, alert_type="inventory_critical", severity="emergency",
              title="RM-SALT stock depleted", message="Raw material 'Salt' is at 0 units — production halt risk."),
        Alert(factory_id=fid, alert_type="machine_down", severity="critical",
              title="Reactor C2 is down", message="Machine M-302 reported down — production line C impacted."),
        Alert(factory_id=fid, alert_type="quality_failure", severity="critical",
              title="OQC failure — Apple Juice batch", message="Defect rate 12.5% exceeds threshold. NCR-001 opened."),
        Alert(factory_id=fid, alert_type="maintenance_overdue", severity="warning",
              title="PM overdue: M-202", message="Preventive maintenance on Labeler B2 is 3 days overdue."),
        Alert(factory_id=fid, alert_type="sales_at_risk", severity="warning",
              title="Sales order at risk", message="ORD-...-001 rush order required delivery in 2 days."),
        Alert(factory_id=fid, alert_type="system", severity="info",
              title="EMICP ready", message="All systems operational."),
    ])

    # ---------- Decisions ----------
    db.add_all([
        Decision(factory_id=fid, decision_type="approve_po",
                 title="Approve PO for RM-PET restock",
                 description="MRP recommends ordering 2000kg PET resin to cover next 14-day demand.",
                 recommendation="APPROVE — supplier rating 5/5, on-time delivery 96%.",
                 priority="high",
                 impact_summary={"cost_egp": "2900", "covers_days": "14"}),
        Decision(factory_id=fid, decision_type="reschedule_order",
                 title="Reschedule Apple Juice order ORD-...-003",
                 description="Order requires delivery in 2 days; line C is down.",
                 recommendation="MOVE to line A with 0.5 day delay; notify customer.",
                 priority="urgent",
                 impact_summary={"delay_days": "0.5", "at_risk_value_egp": "28000"}),
        Decision(factory_id=fid, decision_type="accept_rush",
                 title="Accept rush order from Hypermarket Co",
                 description="Rush order for 5000 BTL-500, 48-hour delivery.",
                 recommendation="ACCEPT with 12% rush surcharge; assign to line A night shift.",
                 priority="urgent",
                 impact_summary={"revenue_egp": "6875", "ot_hours": "16"}),
    ])

    # ---------- App Settings ----------
    db.add_all([
        AppSetting(key="default_factory_id", value=str(fid), description="Active factory on startup"),
        AppSetting(key="language",          value="en",       description="UI language"),
        AppSetting(key="auto_backup",       value="true",     description="Auto backup on schedule"),
        AppSetting(key="backup_time",       value="23:00",    description="Daily backup time"),
        AppSetting(key="backup_keep",       value="30",       description="Backups to keep"),
        AppSetting(key="theme",             value="light",    description="UI theme"),
    ])

    db.commit()
    logger.info("Demo data seeded successfully")
    return {"seeded": True, "factory_id": fid}
