import { useState } from "react"
import { useNavigate, useLocation, useParams } from "react-router-dom"
import {
  LayoutDashboard, Database, ChevronDown, TrendingUp, Factory as FactoryIcon,
  Package, ShoppingCart, CheckCircle, Warehouse, Wrench, Users, DollarSign,
  BarChart2, FileText, Settings, ChevronLeft, ChevronRight, Building2, Grid3x3,
} from "lucide-react"
import { useAppStore } from "@/stores/appStore"
import { cn } from "@/utils/cn"
import { Badge } from "@/components/ui/Badge"
import { FACTORY_TYPES } from "@/constants"

interface NavItem {
  label: string
  path: string
  icon: React.ReactNode
}

const MASTER_ITEMS: NavItem[] = [
  { label: "Production Lines", path: "master-data/production-lines", icon: <Grid3x3 className="w-4 h-4" /> },
  { label: "Machines", path: "master-data/machines", icon: <FactoryIcon className="w-4 h-4" /> },
  { label: "Shifts", path: "master-data/shifts", icon: <Users className="w-4 h-4" /> },
  { label: "Products", path: "master-data/products", icon: <Package className="w-4 h-4" /> },
  { label: "BOM / Recipes", path: "master-data/bom", icon: <Database className="w-4 h-4" /> },
  { label: "Raw Materials", path: "master-data/raw-materials", icon: <Package className="w-4 h-4" /> },
  { label: "Suppliers", path: "master-data/suppliers", icon: <ShoppingCart className="w-4 h-4" /> },
  { label: "Customers", path: "master-data/customers", icon: <Users className="w-4 h-4" /> },
  { label: "Warehouses", path: "master-data/warehouses", icon: <Warehouse className="w-4 h-4" /> },
]

const TOP_ITEMS: NavItem[] = [
  { label: "Dashboard", path: "dashboard", icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: "Sales Planning", path: "sales", icon: <TrendingUp className="w-4 h-4" /> },
  { label: "Production", path: "production", icon: <FactoryIcon className="w-4 h-4" /> },
  { label: "Inventory", path: "inventory", icon: <Package className="w-4 h-4" /> },
  { label: "Procurement", path: "procurement", icon: <ShoppingCart className="w-4 h-4" /> },
  { label: "Quality", path: "quality", icon: <CheckCircle className="w-4 h-4" /> },
  { label: "Warehouse", path: "warehouse", icon: <Warehouse className="w-4 h-4" /> },
  { label: "Maintenance", path: "maintenance", icon: <Wrench className="w-4 h-4" /> },
  { label: "Workforce", path: "workforce", icon: <Users className="w-4 h-4" /> },
  { label: "Cost & Profit", path: "cost", icon: <DollarSign className="w-4 h-4" /> },
  { label: "KPI Center", path: "kpis", icon: <BarChart2 className="w-4 h-4" /> },
  { label: "Reports", path: "reports", icon: <FileText className="w-4 h-4" /> },
  { label: "Settings", path: "settings", icon: <Settings className="w-4 h-4" /> },
]

export function Sidebar({ collapsed }: { collapsed: boolean }) {
  const navigate = useNavigate()
  const location = useLocation()
  const params = useParams()
  const factoryId = params.factoryId ?? useAppStore.getState().currentFactoryId
  const currentFactory = useAppStore((s) => s.currentFactory)
  const factories = useAppStore((s) => s.factories)
  const setCurrentFactory = useAppStore((s) => s.setCurrentFactory)
  const toggleSidebar = useAppStore((s) => s.toggleSidebar)
  const [masterOpen, setMasterOpen] = useState(true)

  const fullPath = (p: string) => `/factory/${factoryId}/${p}`

  const isActive = (p: string) =>
    location.pathname === fullPath(p) ||
    (p === "dashboard" && location.pathname === `/factory/${factoryId}`)

  const goFactory = (id: number) => {
    const f = factories.find((x) => x.id === id)
    if (f) { setCurrentFactory(f); navigate(`/factory/${id}/dashboard`) }
  }

  return (
    <aside
      className={cn(
        "bg-sidebar text-slate-300 flex flex-col shrink-0 transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Factory header */}
      <div className="px-3 py-3 border-b border-slate-800">
        {collapsed ? (
          <div className="flex justify-center">
            <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
              <Building2 className="w-5 h-5" />
            </div>
          </div>
        ) : (
          <div>
            <p className="text-sm font-semibold text-white truncate">{currentFactory?.name ?? "Factory"}</p>
            {currentFactory && (
              <Badge variant="outline" size="sm" className="mt-1 border-slate-700 text-slate-400">
                {FACTORY_TYPES.find((t) => t.value === currentFactory.type)?.label.split(" ")[0]}
              </Badge>
            )}
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-0.5">
        <NavLink item={TOP_ITEMS[0]} active={isActive("dashboard")} collapsed={collapsed} onClick={() => navigate(fullPath("dashboard"))} />
        <div>
          <button
            onClick={() => setMasterOpen((o) => !o)}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium hover:bg-sidebar-hover hover:text-white transition-colors",
              collapsed && "justify-center"
            )}
          >
            <Database className="w-4 h-4" />
            {!collapsed && <span className="flex-1 text-left">Master Data</span>}
            {!collapsed && <ChevronDown className={cn("w-4 h-4 transition-transform", masterOpen && "rotate-180")} />}
          </button>
          {masterOpen && !collapsed && (
            <div className="ml-4 mt-0.5 space-y-0.5 border-l border-slate-800 pl-2">
              {MASTER_ITEMS.map((it) => (
                <NavLink key={it.path} item={it} active={isActive(it.path)} collapsed={false} onClick={() => navigate(fullPath(it.path))} small />
              ))}
            </div>
          )}
        </div>
        {TOP_ITEMS.slice(1).map((it) => (
          <NavLink key={it.path} item={it} active={isActive(it.path)} collapsed={collapsed} onClick={() => navigate(fullPath(it.path))} />
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-slate-800 p-2 space-y-1">
        <button
          onClick={() => navigate("/hub")}
          className={cn(
            "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm hover:bg-sidebar-hover hover:text-white transition-colors",
            collapsed && "justify-center"
          )}
        >
          <Building2 className="w-4 h-4" />
          {!collapsed && <span>Factory Hub</span>}
        </button>
        {!collapsed && factories.length > 1 && (
          <select
            value={String(factoryId)}
            onChange={(e) => goFactory(Number(e.target.value))}
            className="w-full h-8 rounded-lg bg-slate-800 text-slate-200 text-xs px-2 border border-slate-700 focus:outline-none"
          >
            {factories.map((f) => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
        )}
        <button
          onClick={toggleSidebar}
          className={cn(
            "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm hover:bg-sidebar-hover hover:text-white transition-colors",
            collapsed && "justify-center"
          )}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          {!collapsed && <span>Collapse</span>}
        </button>
      </div>
    </aside>
  )
}

function NavLink({
  item, active, collapsed, onClick, small,
}: { item: NavItem; active: boolean; collapsed: boolean; onClick: () => void; small?: boolean }) {
  return (
    <button
      onClick={onClick}
      title={collapsed ? item.label : undefined}
      className={cn(
        "w-full flex items-center gap-3 px-3 rounded-lg text-sm transition-colors",
        small ? "py-1.5" : "py-2",
        active ? "bg-primary text-white font-medium" : "hover:bg-sidebar-hover hover:text-white",
        collapsed && "justify-center"
      )}
    >
      {item.icon}
      {!collapsed && <span className="truncate">{item.label}</span>}
    </button>
  )
}
