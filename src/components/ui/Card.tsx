import { cn } from "@/utils/cn"

interface CardProps {
  title?: string
  subtitle?: string
  headerAction?: React.ReactNode
  children: React.ReactNode
  className?: string
  padding?: boolean
}

export function Card({ title, subtitle, headerAction, children, className, padding = true }: CardProps) {
  return (
    <div className={cn("card", className)}>
      {(title || headerAction) && (
        <div className="flex items-start justify-between px-4 py-3 border-b border-border">
          <div>
            {title && <h3 className="text-sm font-semibold text-slate-900">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {headerAction}
        </div>
      )}
      <div className={cn(padding && "p-4")}>{children}</div>
    </div>
  )
}
