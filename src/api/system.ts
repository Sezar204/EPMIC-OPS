system.ts
Input
import { api } from "./client"
import type { ApiResponse, BackupInfo } from "@/types"

export const systemApi = {
  getHealth:      () => api.get<unknown>("/system/health"),
  getInfo:        () => api.get<ApiResponse<unknown>>("/system/info"),
  getSettings:    () => api.get<ApiResponse<Record<string,string>>>("/system/settings"),
  updateSettings: (d: object) =>
                    api.put<ApiResponse<Record<string,string>>>("/system/settings", d),
  backupNow:      () => api.post<ApiResponse<BackupInfo>>("/system/backup/now"),
  listBackups:    () => api.get<ApiResponse<BackupInfo[]>>("/system/backup/list"),
  restoreBackup:  (filename: string) =>
                    api.post<ApiResponse<null>>(`/system/backup/restore/${filename}`),
  integrityCheck: () => api.get<ApiResponse<unknown>>("/system/integrity-check"),
}

export const corporateApi = {
  getOverview:          () => api.get<ApiResponse<unknown>>("/corporate/overview"),
  getCriticalAlerts:    () => api.get<ApiResponse<unknown[]>>("/corporate/critical-alerts"),
  getPendingDecisions:  () => api.get<ApiResponse<unknown[]>>("/corporate/pending-decisions"),
  getGroupKPIs:         () => api.get<ApiResponse<unknown>>("/corporate/group-kpis"),
}

export const enginesApi = {
  runAll:       (factoryId: number) => api.post<ApiResponse<unknown>>(`/engines/run/all/${factoryId}`),
  runMRP:       (factoryId: number) => api.post<ApiResponse<unknown>>(`/engines/run/mrp/${factoryId}`),
  runAlerts:    (factoryId: number) => api.post<ApiResponse<unknown>>(`/engines/run/alerts/${factoryId}`),
  runInventory: (factoryId: number) => api.post<ApiResponse<unknown>>(`/engines/run/inventory/${factoryId}`),
  runDemand:    (factoryId: number) => api.post<ApiResponse<unknown>>(`/engines/run/demand/${factoryId}`),
  runCapacity:  (factoryId: number) => api.post<ApiResponse<unknown>>(`/engines/run/capacity/${factoryId}`),
  simulate:     (factoryId: number, payload: object) => api.post<ApiResponse<unknown>>(`/engines/simulate/what-if/${factoryId}`, payload),
}

export const salesApi = {
  listOrders:    (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/sales/orders/`),
  getOrder:      (factoryId: number, id: number)  => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/sales/orders/${id}`),
  createOrder:   (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/sales/orders/`, d),
  updateOrder:   (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/sales/orders/${id}`, d),
  removeOrder:   (factoryId: number, id: number)  => api.delete<ApiResponse<null>>(`/factories/${factoryId}/sales/orders/${id}`),
  runCTP:        (factoryId: number, id: number)  => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/sales/orders/${id}/ctp-analysis`),
  listForecasts: (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/sales/forecasts/`),
  saveForecasts: (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/sales/forecasts/`, d),
  getSOP:        (factoryId: number)              => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/sales/sop/`),
}

export const productionApi = {
  listOrders:        (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/production/orders/`),
  createOrder:       (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/production/orders/`, d),
  updateOrder:       (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/production/orders/${id}`, d),
  removeOrder:       (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/production/orders/${id}`),
  dailySchedule:     (factoryId: number, date: string) => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/production/schedule/daily?date=${date}`),
  weeklySchedule:    (factoryId: number, week: string) => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/production/schedule/weekly?week=${week}`),
  capacityAnalysis:  (factoryId: number)         => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/production/capacity/analysis`),
}

export const inventoryApi = {
  rawMaterials:    (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/inventory/raw-materials/`),
  finishedGoods:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/inventory/finished-goods/`),
  wip:             (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/inventory/wip/`),
  abcxyz:          (factoryId: number)         => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/inventory/analysis/abc-xyz`),
  criticalItems:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/inventory/analysis/critical-items`),
  coverage:        (factoryId: number)         => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/inventory/analysis/coverage`),
}

export const procurementApi = {
  listPOs:        (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/procurement/purchase-orders/`),
  getPO:          (factoryId: number, id: number)  => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/procurement/purchase-orders/${id}`),
  createPO:       (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/procurement/purchase-orders/`, d),
  updatePO:       (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/procurement/purchase-orders/${id}`, d),
  removePO:       (factoryId: number, id: number)  => api.delete<ApiResponse<null>>(`/factories/${factoryId}/procurement/purchase-orders/${id}`),
  requirements:   (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/procurement/requirements/`),
  supplierPerf:   (factoryId: number)              => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/procurement/suppliers/performance`),
}

export const qualityApi = {
  listChecks: (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/quality/checks/`),
  createCheck: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/quality/checks/`, d),
  listNCR:     (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/quality/ncr/`),
  createNCR:   (factoryId: number, d: object)  => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/quality/ncr/`, d),
  listCAPA:    (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/quality/capa/`),
  createCAPA:  (factoryId: number, d: object)  => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/quality/capa/`, d),
  metrics:     (factoryId: number)              => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/quality/metrics/`),
}

export const maintenanceApi = {
  listSchedules:   (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/maintenance/schedules/`),
  createSchedule:  (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/maintenance/schedules/`, d),
  listWorkOrders:  (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/maintenance/work-orders/`),
  createWorkOrder: (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/maintenance/work-orders/`, d),
  updateWorkOrder: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/maintenance/work-orders/${id}`, d),
  listBreakdowns:  (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/maintenance/breakdowns/`),
  createBreakdown: (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/maintenance/breakdowns/`, d),
  metrics:         (factoryId: number)              => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/maintenance/metrics/`),
}

export const workforceApi = {
  listWorkers:    (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/workforce/workers/`),
  createWorker:   (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/workforce/workers/`, d),
  updateWorker:   (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/workforce/workers/${id}`, d),
  removeWorker:   (factoryId: number, id: number)  => api.delete<ApiResponse<null>>(`/factories/${factoryId}/workforce/workers/${id}`),
  listShiftAssignments: (factoryId: number)        => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/workforce/shift-assignments/`),
  saveShiftAssignment:  (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/workforce/shift-assignments/`, d),
  listAttendance: (factoryId: number, date: string) => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/workforce/attendance/?date=${date}`),
  saveAttendance: (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/workforce/attendance/`, d),
  metrics:        (factoryId: number)              => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/workforce/metrics/`),
}

export const costApi = {
  listProductCosts:    (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/cost/product-costs/`),
  saveProductCost:     (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/cost/product-costs/`, d),
  varianceAnalysis:    (factoryId: number)              => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/cost/analysis/variance`),
  profitability:       (factoryId: number)              => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/cost/analysis/profitability`),
}

export const kpisApi = {
  list:        (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/kpis/`),
  byCategory:  (factoryId: number, category: string) => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/kpis/${category}`),
  createCustom:(factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/kpis/custom/`, d),
}

export const alertsApi = {
  list:    (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/alerts/`),
  markRead:    (factoryId: number, id: number) => api.put<ApiResponse<null>>(`/factories/${factoryId}/alerts/${id}/read`),
  resolve:     (factoryId: number, id: number) => api.put<ApiResponse<null>>(`/factories/${factoryId}/alerts/${id}/resolve`),
}

export const decisionsApi = {
  pending:    (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/decisions/pending`),
  approve:    (factoryId: number, id: number)  => api.put<ApiResponse<null>>(`/factories/${factoryId}/decisions/${id}/approve`),
  reject:     (factoryId: number, id: number, notes: string) => api.put<ApiResponse<null>>(`/factories/${factoryId}/decisions/${id}/reject`, { notes }),
}

export const reportsApi = {
  library:    (factoryId: number)              => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/reports/library`),
  generate:   (factoryId: number, d: object)   => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/reports/generate`, d),
}
