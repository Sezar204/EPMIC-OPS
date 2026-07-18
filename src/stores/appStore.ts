Input
import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { Factory, Alert } from "@/types"

interface Notif {
  id: number
  message: string
  type: "success" | "error" | "warning" | "info"
}

interface Store {
  backendReady: boolean
  setBackendReady: (v: boolean) => void

  currentFactory: Factory | null
  currentFactoryId: number | null
  setCurrentFactory: (f: Factory | null) => void

  factories: Factory[]
  setFactories: (f: Factory[]) => void

  alerts: Alert[]
  unreadCount: number
  criticalCount: number
  setAlerts: (a: Alert[]) => void

  sidebarCollapsed: boolean
  toggleSidebar: () => void

  settings: Record<string, string>
  setSettings: (s: Record<string, string>) => void

  lastBackupAt: string | null
  lastBackupStatus: "success" | "failed" | null
  setLastBackup: (at: string, status: "success" | "failed") => void

  notification: Notif | null
  notify: (message: string, type: Notif["type"]) => void
  clearNotif: () => void

  isLoading: boolean
  setLoading: (v: boolean) => void
}

export const useAppStore = create<Store>()(
  persist(
    (set) => ({
      backendReady: false,
      setBackendReady: (v) => set({ backendReady: v }),

      currentFactory: null,
      currentFactoryId: null,
      setCurrentFactory: (f) =>
        set({ currentFactory: f, currentFactoryId: f?.id ?? null }),

      factories: [],
      setFactories: (f) => set({ factories: f }),

      alerts: [],
      unreadCount: 0,
      criticalCount: 0,
      setAlerts: (a) =>
        set({
          alerts: a,
          unreadCount:  a.filter((x) => !x.is_read).length,
          criticalCount: a.filter(
            (x) => !x.is_resolved &&
              (x.severity === "critical" || x.severity === "emergency")
          ).length,
        }),

      sidebarCollapsed: false,
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

      settings: {},
      setSettings: (s) => set({ settings: s }),

      lastBackupAt: null,
      lastBackupStatus: null,
      setLastBackup: (at, status) =>
        set({ lastBackupAt: at, lastBackupStatus: status }),

      notification: null,
      notify: (message, type) =>
        set({ notification: { id: Date.now(), message, type } }),
      clearNotif: () => set({ notification: null }),

      isLoading: false,
      setLoading: (v) => set({ isLoading: v }),
    }),
    {
      name: "emicp-store",
      partialize: (s) => ({
        currentFactoryId: s.currentFactoryId,
        sidebarCollapsed: s.sidebarCollapsed,
        lastBackupAt:     s.lastBackupAt,
        settings:         s.settings,
      }),
    }
  )
)
