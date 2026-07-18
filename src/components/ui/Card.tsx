Input
import { HTMLAttributes, ReactNode } from "react"
import { cn } from "@/utils/cn"

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string
  subtitle?: string
  headerAction?: ReactNode
  padding?: "none" | "sm" | "md" | "lg"
}

const PAD = { none: "", sm: "p-3", md: "p-4", lg: "p-6" }

export function Card({ className, title, subtitle, headerAction, padding = "md", children, ...props }: CardProps) {
  const hasHeader = title || subtitle || headerAction
  return (
    <div className={cn("card", className)} {...props}>
      {hasHeader && (
        <div className="flex items-start justify-between px-4 py-3 border-b border-slate-200">
          <div>
            {title    && <h3 className="text-sm font-semibold text-slate-900">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {headerAction}
        </div>
      )}
      <div className={PAD[padding]}>{children}</div>
    </div>
  )
}

export default Card
