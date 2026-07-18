import { useEffect } from "react"
import { CheckCircle2, XCircle, AlertTriangle, Info, X } from "lucide-react"
import { useAppStore } from "@/stores/appStore"
import { cn } from "@/utils/cn"

const config: Record<string, { icon: React.ReactNode; cls: string }> = {
  success: { icon: <CheckCircle2 className="w-5 h-5 text-green-600" />, cls: "border-l-green-500" },
  error:   { icon: <XCircle className="w-5 h-5 text-red-600" />, cls: "border-l-red-500" },
  warning: { icon: <AlertTriangle className="w-5 h-5 text-yellow-600" />, cls: "border-l-yellow-500" },
  info:    { icon: <Info className="w-5 h-5 text-blue-600" />, cls: "border-l-blue-500" },
}

export function Notification() {
  const notification = useAppStore((s) => s.notification)
  const clearNotif = useAppStore((s) => s.clearNotif)

  useEffect(() => {
    if (!notification) return
    const t = setTimeout(() => clearNotif(), 4000)
    return () => clearTimeout(t)
  }, [notification, clearNotif])

  if (!notification) return null
  const c = config[notification.type] ?? config.info

  return (
    <div className="fixed bottom-6 right-6 z-[70] animate-fade-in">
      <div className={cn("card flex items-center gap-3 pl-4 pr-3 py-3 border-l-4 shadow-lg min-w-[280px] max-w-sm", c.cls)}>
        {c.icon}
        <p className="text-sm text-slate-700 flex-1">{notification.message}</p>
        <button onClick={clearNotif} className="text-slate-400 hover:text-slate-700">
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
