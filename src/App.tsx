import { useEffect, useState, useCallback, lazy, Suspense } from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { SplashScreen }  from "@/components/desktop/SplashScreen"
import { AppShell }      from "@/components/layout/AppShell"
import { PageSkeleton }  from "@/components/ui/PageSkeleton"
import { useAppStore }   from "@/stores/appStore"
import { api }           from "@/api/client"
import { factoriesApi }  from "@/api/factories"
import { systemApi }     from "@/api/system"

const Hub               = lazy(() => import("@/pages/hub/ManufacturingHub"))
const Corporate         = lazy(() => import("@/pages/corporate/CorporateCenter"))
const Dashboard         = lazy(() => import("@/pages/factory/dashboard/FactoryDashboard"))
const ProductionLines   = lazy(() => import("@/pages/factory/master-data/ProductionLines"))
const Machines          = lazy(() => import("@/pages/factory/master-data/Machines"))
const Shifts            = lazy(() => import("@/pages/factory/master-data/Shifts"))
const Products          = lazy(() => import("@/pages/factory/master-data/Products"))
const BOM               = lazy(() => import("@/pages/factory/master-data/BOM"))
const RawMaterials      = lazy(() => import("@/pages/factory/master-data/RawMaterials"))
const Suppliers         = lazy(() => import("@/pages/factory/master-data/Suppliers"))
const Customers         = lazy(() => import("@/pages/factory/master-data/Customers"))
const Warehouses        = lazy(() => import("@/pages/factory/master-data/Warehouses"))
const Sales             = lazy(() => import("@/pages/factory/sales/SalesPlanning"))
const Production        = lazy(() => import("@/pages/factory/production/ProductionPlanning"))
const Inventory         = lazy(() => import("@/pages/factory/inventory/Inventory"))
const Procurement       = lazy(() => import("@/pages/factory/procurement/Procurement"))
const Quality           = lazy(() => import("@/pages/factory/quality/Quality"))
const Warehouse         = lazy(() => import("@/pages/factory/warehouse/Warehouse"))
const Maintenance       = lazy(() => import("@/pages/factory/maintenance/Maintenance"))
const Workforce         = lazy(() => import("@/pages/factory/workforce/Workforce"))
const Cost              = lazy(() => import("@/pages/factory/cost/Cost"))
const KPIs              = lazy(() => import("@/pages/factory/kpis/KPICenter"))
const Reports           = lazy(() => import("@/pages/factory/reports/Reports"))
const Settings          = lazy(() => import("@/pages/factory/settings/Settings"))

export default function App() {
  const [splashDone, setSplashDone] = useState(false)
  const [appReady,   setAppReady]   = useState(false)
  const { setBackendReady, setFactories, setSettings, setLastBackup } = useAppStore()

  const init = useCallback(async () => {
    let tries = 0
    while (tries < 30) {
      if (await api.checkHealth()) break
      await new Promise((r) => setTimeout(r, 1000))
      tries++
    }
    setBackendReady(true)

    try {
      const [settingsRes, factoriesRes, backupsRes] = await Promise.allSettled([
        systemApi.getSettings(),
        factoriesApi.getAll(),
        systemApi.listBackups(),
      ])

      if (settingsRes.status === "fulfilled" && settingsRes.value?.data) {
        setSettings(settingsRes.value.data)
      }
      if (factoriesRes.status === "fulfilled" && factoriesRes.value?.data) {
        setFactories(factoriesRes.value.data as any[])
      }
      if (backupsRes.status === "fulfilled" && backupsRes.value?.data) {
        const backups = backupsRes.value.data as any[]
        if (backups.length > 0) {
          setLastBackup(backups[0].created_at, backups[0].status)
        }
      }
    } catch (e) {
      console.error("Init error:", e)
    }

    setAppReady(true)
  }, [setBackendReady, setFactories, setSettings, setLastBackup])

  const onSplashReady = useCallback(() => {
    setSplashDone(true)
    init()
  }, [init])

  if (!splashDone) return <SplashScreen onReady={onSplashReady} />
  if (!appReady)   return <div className="fixed inset-0 bg-slate-900" />

  return (
    <BrowserRouter>
      <AppShell>
        <Suspense fallback={<PageSkeleton />}>
          <Routes>
            <Route path="/"          element={<Navigate to="/hub" replace />} />
            <Route path="/hub"       element={<Hub />} />
            <Route path="/corporate" element={<Corporate />} />
            <Route path="/factory/:factoryId">
              <Route index                              element={<Navigate to="dashboard" replace />} />
              <Route path="dashboard"                   element={<Dashboard />} />
              <Route path="master-data/production-lines" element={<ProductionLines />} />
              <Route path="master-data/machines"         element={<Machines />} />
              <Route path="master-data/shifts"           element={<Shifts />} />
              <Route path="master-data/products"         element={<Products />} />
              <Route path="master-data/bom"              element={<BOM />} />
              <Route path="master-data/raw-materials"    element={<RawMaterials />} />
              <Route path="master-data/suppliers"        element={<Suppliers />} />
              <Route path="master-data/customers"        element={<Customers />} />
              <Route path="master-data/warehouses"       element={<Warehouses />} />
              <Route path="sales"                        element={<Sales />} />
              <Route path="production"                   element={<Production />} />
              <Route path="inventory"                    element={<Inventory />} />
              <Route path="procurement"                  element={<Procurement />} />
              <Route path="quality"                      element={<Quality />} />
              <Route path="warehouse"                    element={<Warehouse />} />
              <Route path="maintenance"                  element={<Maintenance />} />
              <Route path="workforce"                    element={<Workforce />} />
              <Route path="cost"                         element={<Cost />} />
              <Route path="kpis"                         element={<KPIs />} />
              <Route path="reports"                      element={<Reports />} />
              <Route path="settings"                     element={<Settings />} />
            </Route>
            <Route path="*" element={<Navigate to="/hub" replace />} />
          </Routes>
        </Suspense>
      </AppShell>
    </BrowserRouter>
  )
}
