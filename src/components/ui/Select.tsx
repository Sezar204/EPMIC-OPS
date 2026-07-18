import { forwardRef, useId } from "react"
import { ChevronDown } from "lucide-react"
import { cn } from "@/utils/cn"

export interface SelectOption {
  value: string
  label: string
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options: SelectOption[]
  placeholder?: string
  required?: boolean
  onValueChange?: (value: string) => void
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, options, placeholder, required, id, onValueChange, onChange, ...props }, ref) => {
    const generatedId = useId()
    const selectId = id ?? generatedId
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={selectId} className="block text-sm font-medium text-slate-700 mb-1">
            {label}
            {required && <span className="text-danger ml-0.5">*</span>}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            className={cn(
              "w-full h-9 rounded-lg border bg-white px-3 pr-9 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary/30 appearance-none",
              error ? "border-danger focus:ring-danger/30" : "border-border",
              className
            )}
            onChange={(e) => {
              onChange?.(e)
              onValueChange?.(e.target.value)
            }}
            {...props}
          >
            {placeholder && <option value="">{placeholder}</option>}
            {options.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
        </div>
        {error && <p className="mt-1 text-xs text-danger">{error}</p>}
      </div>
    )
  }
)
Select.displayName = "Select"
