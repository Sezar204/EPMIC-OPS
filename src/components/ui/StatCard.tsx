Input
import { ReactNode } from "react"
import { TrendingUp, TrendingDown } from "lucide-react"
import { cn } from "@/utils/cn"

interface Props {
  label: string
  value: string | number
  unit?: string
  icon?: ReactNode
  color?: "primary" | "success" | "warning" | "danger" | "info" | "muted"
  trend?: "up" | "down" | "flat"
  trendValue?: string
  onClick?: () => void
}

const COLOR_BG: Record<NonNullable<Props["color"]>, string> = {
  primary: "bg-blue-100 text-primary",
  success: "bg-green-100 text-success",
  warning: "bg-yellow-100 text-warning",
  danger:  "bg-red-100 text-danger",
  info:    "bg-cyan-100 text-info",
  muted:   "bg-slate-100 text-slate-600",
}

export function StatCard({
  label, value, unit, icon, color = "primary",
  trend, trendValue, onClick,
}: Props) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "card p-4 flex flex-col gap-3",
        onClick && "cursor-pointer hover:shadow-md transition-shadow"
      )}
    >
      <div className="flex items-start justify-between">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${COLOR_BG[color]}`}>
          {icon}
        </div>
        {trend && (
          <div className={cn(
            "flex items-center gap-0.5 text-[11px] font-medium",
            trend === "up"   && "text-green-600",
            trend === "down" && "text-red-600",
            trend === "flat" && "text-slate-500"
          )}>
            {trend === "up"   && <TrendingUp   className="w-3 h-3" />}
            {trend === "down" && <TrendingDown className="w-3 h-3" />}
            {trendValue}
          </div>
        )}
      </div>
      <div>
        <div className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</div>
        <div className="flex items-baseline gap-1 mt-1">
          <span className="text-2xl font-bold text-slate-900">{value}</span>
          {unit && <span className="text-xs text-slate-500">{unit}</span>}
        </div>
      </div>
    </div>
  )
}

export default StatCard
