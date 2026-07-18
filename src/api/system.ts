import { api } from "./client"
import type { ApiResponse, BackupInfo } from "@/types"

export const systemApi = {
  getHealth:      () => api.get<any>("/system/health"),
  getInfo:        () => api.get<ApiResponse<any>>("/system/info"),
  getSettings:    () => api.get<ApiResponse<Record<string,string>>>("/system/settings"),
  updateSettings: (d: object) =>
    api.put<ApiResponse<Record<string,string>>>("/system/settings", d),
  backupNow:      () => api.post<ApiResponse<BackupInfo>>("/system/backup/now"),
  listBackups:    () => api.get<ApiResponse<BackupInfo[]>>("/system/backup/list"),
  restoreBackup:  (filename: string) =>
    api.post<ApiResponse<null>>(`/system/backup/restore/${filename}`),
  integrityCheck: () => api.get<ApiResponse<any>>("/system/integrity-check"),
}
