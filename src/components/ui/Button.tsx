Input
import { ButtonHTMLAttributes, forwardRef, ReactNode } from "react"
import { Loader2 } from "lucide-react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils/cn"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary/30",
  {
    variants: {
      variant: {
        default:  "bg-primary text-white hover:bg-primary/90",
        outline:  "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50",
        ghost:    "text-slate-700 hover:bg-slate-100",
        danger:   "bg-danger text-white hover:bg-danger/90",
        success:  "bg-success text-white hover:bg-success/90",
        secondary:"bg-slate-800 text-white hover:bg-slate-700",
      },
      size: {
        sm: "h-8 px-3 text-xs",
        md: "h-9 px-4 text-sm",
        lg: "h-10 px-5 text-sm",
      },
    },
    defaultVariants: { variant: "default", size: "md" },
  }
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, leftIcon, rightIcon, children, disabled, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : leftIcon}
      {children}
      {!loading && rightIcon}
    </button>
  )
)
Button.displayName = "Button"

export default Button
