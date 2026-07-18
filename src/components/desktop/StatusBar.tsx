import { useEffect, useState } from "react"
import { Database, Circle } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import { useAppStore } from "@/stores/appStore"

export function StatusBar() {
  const lastBackupAt = useAppStore((s) => s.lastBackupAt)
  const lastBackupStatus = useAppStore((s) => s.lastBackupStatus)
  const backendReady = useAppStore((s) => s.backendReady)
  const [now, setNow] = useState(new Date())

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  let backupLabel = "No backup yet"
  let backupColor = "text-slate-400"
  if (lastBackupAt) {
    try {
      const ageMs = now.getTime() - new Date(lastBackupAt).getTime()
      const hours = ageMs / 3_600_000
      backupColor = hours < 24 ? "text-green-400" : "text-yellow-400"
      const word = lastBackupStatus === "success" ? "" : " (failed)"
      backupLabel = `Last backup: ${formatDistanceToNow(new Date(lastBackupAt), { addSuffix: true })}${word}`
    } catch { backupLabel = "Last backup: unknown" }
  }

  return (
    <div className="h-6 flex items-center justify-between bg-secondary px-3 text-[11px] text-slate-400 shrink-0 select-none">
      <div className="flex items-center gap-1.5">
        <Database className="w-3 h-3" />
        <span className={backupColor}>{backupLabel}</span>
      </div>
      <div className="flex items-center gap-1.5">
        <Circle
          className={`w-2.5 h-2.5 ${backendReady ? "text-green-500 fill-green-500" : "text-red-500 fill-red-500"}`}
        />
        <span>{backendReady ? "Connected" : "Disconnected"}</span>
      </div>
      <div className="tabular-nums">
        {now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
      </div>
    </div>
  )
}
