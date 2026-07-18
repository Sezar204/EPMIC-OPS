Input
import { useEffect } from "react"
import { CheckCircle2, XCircle, AlertTriangle, Info, X } from "lucide-react"
import { useAppStore } from "@/stores/appStore"
import { cn } from "@/utils/cn"

const ICONS = {
  success: { Icon: CheckCircle2, color: "text-green-600", bg: "bg-green-50 border-green-200" },
  error:   { Icon: XCircle,      color: "text-red-600",   bg: "bg-red-50 border-red-200" },
  warning: { Icon: AlertTriangle,color: "text-yellow-600",bg: "bg-yellow-50 border-yellow-200" },
  info:    { Icon: Info,         color: "text-cyan-600",  bg: "bg-cyan-50 border-cyan-200" },
}

export function Notification() {
  const notification = useAppStore((s) => s.notification)
  const clearNotif   = useAppStore((s) => s.clearNotif)

  useEffect(() => {
    if (!notification) return
    const t = setTimeout(clearNotif, 4000)
    return () => clearTimeout(t)
  }, [notification, clearNotif])

  if (!notification) return null
  const { Icon, color, bg } = ICONS[notification.type]

  return (
    <div
      key={notification.id}
      className={cn(
        "fixed bottom-12 right-4 z-50",
        "flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border",
        "bg-white animate-in slide-in-from-right duration-300",
        "min-w-[280px] max-w-md"
      )}
    >
      <div className={cn("w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 border", bg)}>
        <Icon className={cn("w-4 h-4", color)} />
      </div>
      <div className="flex-1 text-sm text-slate-800">{notification.message}</div>
      <button
        onClick={clearNotif}
        className="text-slate-400 hover:text-slate-700 p-0.5"
        aria-label="Close"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}

export default Notification
