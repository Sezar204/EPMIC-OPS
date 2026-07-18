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
    api.get<ApiResponse<any>>(`/factories/${id}/dashboard-summary`),
  getCalendar:       (id: number, month: string) =>
    api.get<ApiResponse<any[]>>(`/factories/${id}/calendar?month=${month}`),
  updateCalendar:    (id: number, d: object) =>
    api.post<ApiResponse<any>>(`/factories/${id}/calendar`, d),
}
