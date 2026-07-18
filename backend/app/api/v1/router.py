Input
from fastapi import APIRouter
from app.api.v1.endpoints import (
    system, factories, engines, corporate, import_export,
    alerts, decisions, kpis, reports, sales, production, inventory,
    procurement, quality, maintenance, workforce, cost,
)

api_router = APIRouter()
api_router.include_router(system.router,          prefix="/system",     tags=["System"])
api_router.include_router(factories.router,       prefix="/factories",  tags=["Factories"])
api_router.include_router(engines.router,         prefix="/engines",    tags=["Engines"])
api_router.include_router(corporate.router,       prefix="/corporate",  tags=["Corporate"])
api_router.include_router(import_export.router,   prefix="/import",     tags=["Import/Export"])
api_router.include_router(alerts.router,          prefix="/alerts",     tags=["Alerts"])
api_router.include_router(decisions.router,       prefix="/decisions",  tags=["Decisions"])
api_router.include_router(kpis.router,            prefix="/kpis",       tags=["KPIs"])
api_router.include_router(reports.router,         prefix="/reports",    tags=["Reports"])
api_router.include_router(sales.router,           prefix="/sales",      tags=["Sales"])
api_router.include_router(production.router,      prefix="/production", tags=["Production"])
api_router.include_router(inventory.router,       prefix="/inventory",  tags=["Inventory"])
api_router.include_router(procurement.router,     prefix="/procurement",tags=["Procurement"])
api_router.include_router(quality.router,         prefix="/quality",    tags=["Quality"])
api_router.include_router(maintenance.router,     prefix="/maintenance",tags=["Maintenance"])
api_router.include_router(workforce.router,       prefix="/workforce",  tags=["Workforce"])
api_router.include_router(cost.router,            prefix="/cost",       tags=["Cost"])
