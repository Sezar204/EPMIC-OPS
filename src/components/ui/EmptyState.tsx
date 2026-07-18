import { Inbox } from "lucide-react"
import { Button } from "./Button"

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
}

export function EmptyState({ icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="card flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
        {icon ?? <Inbox className="w-7 h-7" />}
      </div>
      <h3 className="mt-4 text-base font-semibold text-slate-800">{title}</h3>
      {description && <p className="mt-1 text-sm text-slate-500 max-w-sm">{description}</p>}
      {actionLabel && onAction && (
        <Button className="mt-4" onClick={onAction}>{actionLabel}</Button>
      )}
    </div>
  )
}
