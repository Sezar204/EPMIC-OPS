from fastapi import APIRouter

from app.api.v1.endpoints import (
    system, factories, production_lines, machines, shifts,
    products, bom, raw_materials, suppliers, customers,
    warehouses, sales, production, inventory, procurement,
    quality, maintenance, workforce, cost, kpis, alerts,
    decisions, reports, engines, corporate, import_export,
)

api_router = APIRouter()

# Core routers
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(factories.router, prefix="/factories", tags=["Factories"])

# Factory-scoped sub-resource routers (all mounted under /factories)
for mod in [
    production_lines, machines, shifts, products, bom, raw_materials,
    suppliers, customers, warehouses, sales, production, inventory,
    procurement, quality, maintenance, workforce, cost, kpis,
    alerts, decisions, reports,
]:
    api_router.include_router(mod.router, prefix="/factories", tags=[mod.__name__.split(".")[-1]])

# Cross-cutting routers
api_router.include_router(engines.router, prefix="/engines", tags=["Engines"])
api_router.include_router(corporate.router, prefix="/corporate", tags=["Corporate"])
api_router.include_router(import_export.router, prefix="/import", tags=["Import"])
