Input
import { useEffect, useState } from "react"
import { Database, Circle } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import { useAppStore } from "@/stores/appStore"
import { api } from "@/api/client"
import { HEALTH_INTERVAL } from "@/constants"
import { cn } from "@/utils/cn"

export function StatusBar() {
  const lastBackupAt     = useAppStore((s) => s.lastBackupAt)
  const lastBackupStatus = useAppStore((s) => s.lastBackupStatus)
  const backendReady     = useAppStore((s) => s.backendReady)
  const setBackendReady  = useAppStore((s) => s.setBackendReady)

  const [now, setNow] = useState(new Date())

  useEffect(() => {
    const tickClock = setInterval(() => setNow(new Date()), 1000)
    const check     = setInterval(async () => {
      const ok = await api.checkHealth()
      setBackendReady(ok)
    }, HEALTH_INTERVAL)
    return () => { clearInterval(tickClock); clearInterval(check) }
  }, [setBackendReady])

  const backupAgeHours = lastBackupAt
    ? (Date.now() - new Date(lastBackupAt).getTime()) / 36e5
    : Infinity
  const backupColor =
    !lastBackupAt ? "text-slate-400" :
    backupAgeHours < 24 ? "text-green-400" :
    "text-yellow-400"

  return (
    <div className="h-6 bg-slate-900 text-slate-300 flex items-center justify-between px-3 text-[11px] font-mono select-none flex-shrink-0 border-t border-slate-800">
      <div className="flex items-center gap-4">
        <div className={cn("flex items-center gap-1.5", backupColor)}>
          <Database className="w-3 h-3" />
          <span>
            {lastBackupAt
              ? `Last backup: ${formatDistanceToNow(new Date(lastBackupAt), { addSuffix: true })} ${lastBackupStatus === "failed" ? "⚠" : "✓"}`
              : "No backup yet"}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-1.5">
        <Circle
          className={cn("w-2 h-2 fill-current",
            backendReady ? "text-green-400" : "text-red-400")}
        />
        <span className={backendReady ? "text-green-400" : "text-red-400"}>
          {backendReady ? "Connected" : "Disconnected"}
        </span>
      </div>
      <div className="text-slate-400">
        {now.toLocaleTimeString("en-US", { hour12: false })}
      </div>
    </div>
  )
}

export default StatusBar
