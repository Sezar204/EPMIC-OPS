Input
import { useState } from "react"
import { NavLink, useParams, useNavigate } from "react-router-dom"
import {
  LayoutDashboard, Database, TrendingUp, Factory, Package, ShoppingCart,
  CheckCircle, Warehouse as WarehouseIcon, Wrench, Users, DollarSign,
  BarChart2, FileText, Settings, ChevronLeft, ChevronRight, ChevronDown,
  Network, Cog, Clock, Boxes, ListTree, Layers, Truck, UserCircle, Building2,
  Home, AlertTriangle, CircleDot,
} from "lucide-react"
import { useAppStore } from "@/stores/appStore"
import { cn } from "@/utils/cn"

interface Props { collapsed: boolean }

interface NavItem {
  to: string
  label: string
  icon: React.ComponentType<{ className?: string }>
}

interface NavGroup {
  label: string
  icon: React.ComponentType<{ className?: string }>
  children: NavItem[]
}

const MASTER_DATA: NavGroup = {
  label: "Master Data",
  icon: Database,
  children: [
    { to: "master-data/production-lines", label: "Production Lines", icon: Network },
    { to: "master-data/machines",          label: "Machines",          icon: Cog },
    { to: "master-data/shifts",            label: "Shifts",            icon: Clock },
    { to: "master-data/products",          label: "Products",          icon: Boxes },
    { to: "master-data/bom",               label: "BOM / Recipes",     icon: ListTree },
    { to: "master-data/raw-materials",     label: "Raw Materials",     icon: Layers },
    { to: "master-data/suppliers",         label: "Suppliers",         icon: Truck },
    { to: "master-data/customers",         label: "Customers",         icon: UserCircle },
    { to: "master-data/warehouses",        label: "Warehouses",        icon: Building2 },
  ],
}

const TOP: NavItem[] = [
  { to: "dashboard",  label: "Dashboard",        icon: LayoutDashboard },
]

const MIDDLE: NavItem[] = [
  { to: "sales",         label: "Sales Planning",  icon: TrendingUp },
  { to: "production",    label: "Production",      icon: Factory },
  { to: "inventory",     label: "Inventory",       icon: Package },
  { to: "procurement",   label: "Procurement",     icon: ShoppingCart },
  { to: "quality",       label: "Quality",         icon: CheckCircle },
  { to: "warehouse",     label: "Warehouse",       icon: WarehouseIcon },
  { to: "maintenance",   label: "Maintenance",     icon: Wrench },
  { to: "workforce",     label: "Workforce",       icon: Users },
  { to: "cost",          label: "Cost & Profit",   icon: DollarSign },
  { to: "kpis",          label: "KPI Center",      icon: BarChart2 },
  { to: "reports",       label: "Reports",         icon: FileText },
]

const BOTTOM: NavItem[] = [
  { to: "settings", label: "Settings", icon: Settings },
]

export function Sidebar({ collapsed }: Props) {
  const { factoryId } = useParams<{ factoryId: string }>()
  const factory       = useAppStore((s) => s.currentFactory)
  const factories     = useAppStore((s) => s.factories)
  const setFactory    = useAppStore((s) => s.setCurrentFactory)
  const toggleSidebar = useAppStore((s) => s.toggleSidebar)
  const criticalCount = useAppStore((s) => s.criticalCount)
  const navigate      = useNavigate()

  const [masterOpen, setMasterOpen] = useState(true)
  const [switcherOpen, setSwitcherOpen] = useState(false)

  const base = `/factory/${factoryId}`

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    cn(
      "flex items-center gap-2.5 px-3 py-2 text-sm rounded-md transition-colors",
      isActive
        ? "bg-primary text-white font-medium"
        : "text-slate-300 hover:bg-slate-800 hover:text-white"
    )

  const renderItem = (item: NavItem) => {
    const Icon = item.icon
    return (
      <NavLink key={item.to} to={`${base}/${item.to}`} className={linkClass}>
        <Icon className="w-4 h-4 flex-shrink-0" />
        {!collapsed && <span className="truncate">{item.label}</span>}
      </NavLink>
    )
  }

  return (
    <aside
      className={cn(
        "bg-slate-900 text-white flex flex-col flex-shrink-0 transition-all duration-300 ease-in-out border-r border-slate-800",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Factory header */}
      {!collapsed && (
        <div className="p-3 border-b border-slate-800 flex-shrink-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0 flex-1">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Current Factory
              </div>
              <div className="text-sm font-semibold truncate mt-0.5">
                {factory?.name ?? "—"}
              </div>
              {factory && (
                <div className="mt-1.5 flex items-center gap-1.5">
                  <span className="px-1.5 py-0.5 text-[10px] bg-slate-800 text-slate-300 rounded uppercase font-mono">
                    {factory.type}
                  </span>
                  <span className="flex items-center gap-1 text-[10px] text-green-400">
                    <CircleDot className="w-2.5 h-2.5" /> {factory.status}
                  </span>
                </div>
              )}
            </div>
            {criticalCount > 0 && (
              <div className="flex items-center gap-1 text-[10px] bg-red-500/20 text-red-300 px-1.5 py-0.5 rounded font-mono">
                <AlertTriangle className="w-2.5 h-2.5" /> {criticalCount}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Scrollable nav */}
      <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {TOP.map(renderItem)}

        {/* Master data collapsible */}
        <div>
          <button
            onClick={() => setMasterOpen((v) => !v)}
            className={cn(
              "w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-md transition-colors",
              "text-slate-300 hover:bg-slate-800 hover:text-white"
            )}
          >
            <Database className="w-4 h-4 flex-shrink-0" />
            {!collapsed && (
              <>
                <span className="truncate flex-1 text-left">Master Data</span>
                <ChevronDown
                  className={cn("w-3.5 h-3.5 transition-transform",
                    masterOpen ? "" : "-rotate-90")}
                />
              </>
            )}
          </button>
          {!collapsed && masterOpen && (
            <div className="ml-4 pl-2 border-l border-slate-800 space-y-0.5 mt-0.5">
              {MASTER_DATA.children.map(renderItem)}
            </div>
          )}
        </div>

        {MIDDLE.map(renderItem)}
        {BOTTOM.map(renderItem)}
      </nav>

      {/* Bottom: switcher + back + collapse */}
      <div className="p-2 border-t border-slate-800 space-y-1 flex-shrink-0">
        {!collapsed && (
          <div className="relative">
            <button
              onClick={() => setSwitcherOpen((v) => !v)}
              className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-400 hover:text-white hover:bg-slate-800 rounded-md"
            >
              <Factory className="w-3.5 h-3.5" />
              <span className="flex-1 text-left">Switch Factory</span>
              <ChevronDown className={cn("w-3 h-3 transition-transform",
                switcherOpen ? "" : "-rotate-90")} />
            </button>
            {switcherOpen && factories.length > 0 && (
              <div className="absolute bottom-full left-0 right-0 mb-1 bg-slate-800 border border-slate-700 rounded-md max-h-48 overflow-y-auto">
                {factories.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => {
                      setFactory(f)
                      setSwitcherOpen(false)
                      navigate(`/factory/${f.id}/dashboard`)
                    }}
                    className={cn(
                      "w-full text-left px-3 py-1.5 text-xs hover:bg-slate-700",
                      f.id === factory?.id ? "text-primary font-medium" : "text-slate-200"
                    )}
                  >
                    {f.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        <NavLink
          to="/hub"
          className={cn(
            "flex items-center gap-2.5 px-3 py-2 text-sm rounded-md transition-colors",
            "text-slate-400 hover:bg-slate-800 hover:text-white"
          )}
        >
          <Home className="w-4 h-4 flex-shrink-0" />
          {!collapsed && <span>Back to Hub</span>}
        </NavLink>
        <button
          onClick={toggleSidebar}
          className="w-full flex items-center justify-center gap-2 px-3 py-1.5 text-xs text-slate-500 hover:text-white hover:bg-slate-800 rounded-md"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : (
            <><ChevronLeft className="w-4 h-4" /> Collapse</>
          )}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
