Input
import { api } from "./client"
import type { ApiResponse, Factory, FactoryHealthScore } from "@/types"

export const factoriesApi = {
  getAll:            ()            => api.get<ApiResponse<Factory[]>>("/factories"),
  getById:           (id: number)  => api.get<ApiResponse<Factory>>(`/factories/${id}`),
  create:            (d: object)   => api.post<ApiResponse<Factory>>("/factories", d),
  update:            (id: number, d: object) =>
                       api.put<ApiResponse<Factory>>(`/factories/${id}`, d),
  remove:            (id: number)  => api.delete<ApiResponse<null>>(`/factories/${id}`),
  getHealthScore:    (id: number)  =>
                       api.get<ApiResponse<FactoryHealthScore>>(`/factories/${id}/health-score`),
  getDashboard:      (id: number)  =>
                       api.get<ApiResponse<unknown>>(`/factories/${id}/dashboard-summary`),
  getCalendar:       (id: number, month: string) =>
                       api.get<ApiResponse<unknown[]>>(`/factories/${id}/calendar?month=${month}`),
  updateCalendar:    (id: number, d: object) =>
                       api.post<ApiResponse<unknown>>(`/factories/${id}/calendar`, d),
}

export const productionLinesApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/production-lines/`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/production-lines/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/production-lines/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/production-lines/${id}`),
}

export const machinesApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/machines/`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/machines/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/machines/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/machines/${id}`),
}

export const shiftsApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/shifts/`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/shifts/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/shifts/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/shifts/${id}`),
}

export const productsApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/products/`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/products/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/products/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/products/${id}`),
}

export const bomApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/bom/`),
  get:    (factoryId: number, id: number) => api.get<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/bom/${id}`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/bom/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/bom/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/bom/${id}`),
}

export const rawMaterialsApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/raw-materials/`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/raw-materials/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/raw-materials/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/raw-materials/${id}`),
}

export const suppliersApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/suppliers/`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/suppliers/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/suppliers/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/suppliers/${id}`),
}

export const customersApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/customers/`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/customers/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/customers/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/customers/${id}`),
}

export const warehousesApi = {
  list:   (factoryId: number)         => api.get<ApiResponse<unknown[]>>(`/factories/${factoryId}/master-data/warehouses/`),
  create: (factoryId: number, d: object) => api.post<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/warehouses/`, d),
  update: (factoryId: number, id: number, d: object) => api.put<ApiResponse<unknown>>(`/factories/${factoryId}/master-data/warehouses/${id}`, d),
  remove: (factoryId: number, id: number) => api.delete<ApiResponse<null>>(`/factories/${factoryId}/master-data/warehouses/${id}`),
}
