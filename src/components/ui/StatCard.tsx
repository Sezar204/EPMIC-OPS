import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react"
import { cn } from "@/utils/cn"

interface StatCardProps {
  label: string
  value: string | number
  unit?: string
  icon?: React.ReactNode
  color?: "primary" | "success" | "warning" | "danger" | "info"
  trend?: "up" | "down" | "flat"
  trendValue?: string
  onClick?: () => void
}

const colorMap: Record<string, string> = {
  primary: "bg-primary/10 text-primary",
  success: "bg-green-50 text-green-600",
  warning: "bg-yellow-50 text-yellow-600",
  danger:  "bg-red-50 text-red-600",
  info:    "bg-cyan-50 text-cyan-600",
}

export function StatCard({ label, value, unit, icon, color = "primary", trend, trendValue, onClick }: StatCardProps) {
  const TrendIcon = trend === "up" ? ArrowUpRight : trend === "down" ? ArrowDownRight : Minus
  return (
    <div
      onClick={onClick}
      className={cn(
        "card p-4 flex items-center gap-4",
        onClick && "cursor-pointer hover:shadow-md transition-shadow"
      )}
    >
      {icon && (
        <div className={cn("w-11 h-11 rounded-lg flex items-center justify-center shrink-0", colorMap[color])}>
          {icon}
        </div>
      )}
      <div className="min-w-0">
        <p className="text-xs text-slate-500 truncate">{label}</p>
        <p className="text-2xl font-bold text-slate-900 leading-tight">
          {value}
          {unit && <span className="text-sm font-medium text-slate-400 ml-1">{unit}</span>}
        </p>
        {trend && (
          <div className="flex items-center gap-1 text-xs mt-0.5">
            <TrendIcon className={cn(
              "w-3.5 h-3.5",
              trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-slate-400"
            )} />
            <span className={cn(
              trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-slate-400"
            )}>{trendValue}</span>
          </div>
        )}
      </div>
    </div>
  )
}
