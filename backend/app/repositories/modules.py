Input
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session
from app.repositories import BaseRepository
from app.models import (
    Factory, ProductionLine, Machine, Shift, Warehouse, Product, BOMHeader,
    BOMLine, RawMaterial, Customer, SalesOrder, SalesOrderLine, DemandForecast,
    Supplier, SupplierMaterial, PurchaseOrder, PurchaseOrderLine,
    InventoryRawMaterial, InventoryFinishedGoods, InventoryWIP,
    ProductionOrder, QualityCheck, NonConformanceReport, CAPARecord,
    MaintenanceSchedule, MaintenanceWorkOrder, MachineBreakdown,
    Worker, ShiftAssignment, AttendanceRecord, ProductCost,
    KPIDefinition, KPIValue, Alert, Decision, AppSetting, BackupLog,
)


class FactoryRepo(BaseRepository[Factory]):
    def __init__(self, db: Session): super().__init__(db, Factory)


class ProductionLineRepo(BaseRepository[ProductionLine]):
    def __init__(self, db: Session): super().__init__(db, ProductionLine)


class MachineRepo(BaseRepository[Machine]):
    def __init__(self, db: Session): super().__init__(db, Machine)

    def list_by_line(self, line_id: int) -> List[Machine]:
        return list(self.db.scalars(select(Machine).where(Machine.line_id == line_id)).all())


class ShiftRepo(BaseRepository[Shift]):
    def __init__(self, db: Session): super().__init__(db, Shift)


class WarehouseRepo(BaseRepository[Warehouse]):
    def __init__(self, db: Session): super().__init__(db, Warehouse)


class ProductRepo(BaseRepository[Product]):
    def __init__(self, db: Session): super().__init__(db, Product)


class BOMRepo(BaseRepository[BOMHeader]):
    def __init__(self, db: Session): super().__init__(db, BOMHeader)

    def get_with_lines(self, bom_id: int) -> Optional[BOMHeader]:
        bom = self.get(bom_id)
        if bom and bom.lines is not None:
            _ = list(bom.lines)  # force load
        return bom


class RawMaterialRepo(BaseRepository[RawMaterial]):
    def __init__(self, db: Session): super().__init__(db, RawMaterial)


class CustomerRepo(BaseRepository[Customer]):
    def __init__(self, db: Session): super().__init__(db, Customer)


class SalesOrderRepo(BaseRepository[SalesOrder]):
    def __init__(self, db: Session): super().__init__(db, SalesOrder)

    def get_with_lines(self, order_id: int) -> Optional[SalesOrder]:
        so = self.get(order_id)
        if so and so.lines is not None:
            _ = list(so.lines)
        return so


class DemandForecastRepo(BaseRepository[DemandForecast]):
    def __init__(self, db: Session): super().__init__(db, DemandForecast)


class SupplierRepo(BaseRepository[Supplier]):
    def __init__(self, db: Session): super().__init__(db, Supplier)


class PurchaseOrderRepo(BaseRepository[PurchaseOrder]):
    def __init__(self, db: Session): super().__init__(db, PurchaseOrder)

    def get_with_lines(self, po_id: int) -> Optional[PurchaseOrder]:
        po = self.get(po_id)
        if po and po.lines is not None:
            _ = list(po.lines)
        return po


class InventoryRawMaterialRepo(BaseRepository[InventoryRawMaterial]):
    def __init__(self, db: Session): super().__init__(db, InventoryRawMaterial)


class InventoryFinishedGoodsRepo(BaseRepository[InventoryFinishedGoods]):
    def __init__(self, db: Session): super().__init__(db, InventoryFinishedGoods)


class InventoryWIPRepo(BaseRepository[InventoryWIP]):
    def __init__(self, db: Session): super().__init__(db, InventoryWIP)


class ProductionOrderRepo(BaseRepository[ProductionOrder]):
    def __init__(self, db: Session): super().__init__(db, ProductionOrder)


class QualityCheckRepo(BaseRepository[QualityCheck]):
    def __init__(self, db: Session): super().__init__(db, QualityCheck)


class NCRRepo(BaseRepository[NonConformanceReport]):
    def __init__(self, db: Session): super().__init__(db, NonConformanceReport)


class CAPARepo(BaseRepository[CAPARecord]):
    def __init__(self, db: Session): super().__init__(db, CAPARecord)


class MaintenanceScheduleRepo(BaseRepository[MaintenanceSchedule]):
    def __init__(self, db: Session): super().__init__(db, MaintenanceSchedule)


class WorkOrderRepo(BaseRepository[MaintenanceWorkOrder]):
    def __init__(self, db: Session): super().__init__(db, MaintenanceWorkOrder)


class BreakdownRepo(BaseRepository[MachineBreakdown]):
    def __init__(self, db: Session): super().__init__(db, MachineBreakdown)


class WorkerRepo(BaseRepository[Worker]):
    def __init__(self, db: Session): super().__init__(db, Worker)


class ShiftAssignmentRepo(BaseRepository[ShiftAssignment]):
    def __init__(self, db: Session): super().__init__(db, ShiftAssignment)


class AttendanceRepo(BaseRepository[AttendanceRecord]):
    def __init__(self, db: Session): super().__init__(db, AttendanceRecord)


class ProductCostRepo(BaseRepository[ProductCost]):
    def __init__(self, db: Session): super().__init__(db, ProductCost)


class KPIDefinitionRepo(BaseRepository[KPIDefinition]):
    def __init__(self, db: Session): super().__init__(db, KPIDefinition)

    def by_category(self, factory_id: int, category: str) -> List[KPIDefinition]:
        return list(self.db.scalars(
            select(KPIDefinition).where(
                KPIDefinition.factory_id == factory_id,
                KPIDefinition.category == category,
                KPIDefinition.is_active == True,  # noqa: E712
            )
        ).all())


class KPIValueRepo(BaseRepository[KPIValue]):
    def __init__(self, db: Session): super().__init__(db, KPIValue)

    def trend(self, kpi_id: int, factory_id: int, days: int = 30) -> List[KPIValue]:
        from datetime import date, timedelta
        cutoff = date.today() - timedelta(days=days)
        return list(self.db.scalars(
            select(KPIValue)
            .where(KPIValue.kpi_id == kpi_id, KPIValue.factory_id == factory_id,
                   KPIValue.period_date >= cutoff)
            .order_by(KPIValue.period_date.asc())
        ).all())


class AlertRepo(BaseRepository[Alert]):
    def __init__(self, db: Session): super().__init__(db, Alert)


class DecisionRepo(BaseRepository[Decision]):
    def __init__(self, db: Session): super().__init__(db, Decision)

    def pending(self, factory_id: int) -> List[Decision]:
        return list(self.db.scalars(
            select(Decision).where(
                Decision.factory_id == factory_id,
                Decision.status == "pending",
            ).order_by(Decision.priority.desc(), Decision.created_at.desc())
        ).all())


class AppSettingRepo(BaseRepository[AppSetting]):
    def __init__(self, db: Session): super().__init__(db, AppSetting)

    def get_value(self, key: str, default: str = "") -> str:
        s = self.db.scalars(select(AppSetting).where(AppSetting.key == key)).first()
        return s.value if s else default

    def set_value(self, key: str, value: str) -> AppSetting:
        s = self.db.scalars(select(AppSetting).where(AppSetting.key == key)).first()
        if s:
            s.value = value
        else:
            s = AppSetting(key=key, value=value)
            self.db.add(s)
        self.db.flush()
        return s

    def all_dict(self) -> dict:
        return {s.key: s.value for s in self.db.scalars(select(AppSetting)).all()}


class BackupLogRepo(BaseRepository[BackupLog]):
    def __init__(self, db: Session): super().__init__(db, BackupLog)
