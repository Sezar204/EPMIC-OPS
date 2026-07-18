
Input
import { HTMLAttributes, ReactNode } from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils/cn"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full font-medium whitespace-nowrap",
  {
    variants: {
      variant: {
        success: "bg-green-100 text-green-700",
        warning: "bg-yellow-100 text-yellow-700",
        danger:  "bg-red-100 text-red-700",
        info:    "bg-cyan-100 text-cyan-700",
        muted:   "bg-slate-100 text-slate-600",
        outline: "border border-slate-300 text-slate-700 bg-white",
        primary: "bg-blue-100 text-blue-700",
      },
      size: {
        sm: "px-1.5 py-0.5 text-[10px]",
        md: "px-2 py-0.5 text-xs",
      },
    },
    defaultVariants: { variant: "muted", size: "md" },
  }
)

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean
  icon?: ReactNode
}

export function Badge({ className, variant, size, dot, icon, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {dot && <span className="w-1.5 h-1.5 rounded-full bg-current" />}
      {icon}
      {children}
    </span>
  )
}

export default Badge
