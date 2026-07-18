import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils/cn"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full font-medium border",
  {
    variants: {
      variant: {
        success: "bg-green-50 text-green-700 border-green-200",
        warning: "bg-yellow-50 text-yellow-700 border-yellow-200",
        danger:  "bg-red-50 text-red-700 border-red-200",
        info:    "bg-blue-50 text-blue-700 border-blue-200",
        muted:   "bg-slate-100 text-slate-600 border-slate-200",
        outline: "bg-white text-slate-700 border-border",
      },
      size: {
        sm: "px-2 py-0.5 text-[11px]",
        md: "px-2.5 py-1 text-xs",
      },
    },
    defaultVariants: { variant: "muted", size: "md" },
  }
)

interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean
}

export function Badge({ className, variant, size, dot, children, ...props }: BadgeProps) {
  const dotColor: Record<string, string> = {
    success: "bg-green-500",
    warning: "bg-yellow-500",
    danger:  "bg-red-500",
    info:    "bg-blue-500",
    muted:   "bg-slate-400",
    outline: "bg-slate-400",
  }
  return (
    <span className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {dot && <span className={cn("w-1.5 h-1.5 rounded-full", dotColor[variant ?? "muted"])} />}
      {children}
    </span>
  )
}
