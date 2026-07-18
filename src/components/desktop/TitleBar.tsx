Input
import { useEffect, useState } from "react"
import { Factory, Minus, Square, X, Maximize2 } from "lucide-react"
import { APP_NAME } from "@/constants"
import { useAppStore } from "@/stores/appStore"
import { cn } from "@/utils/cn"

export function TitleBar() {
  const factory = useAppStore((s) => s.currentFactory)
  const [isMaximized, setIsMaximized] = useState(false)

  const win = async () => {
    try {
      const mod = await import("@tauri-apps/api/window")
      const w   = mod.getCurrentWindow()
      return { w, mod }
    } catch {
      return null
    }
  }

  const handleMinimize = async () => {
    const h = await win()
    if (h) await h.w.minimize()
  }
  const handleMaximize = async () => {
    const h = await win()
    if (h) {
      const max = await h.w.isMaximized()
      if (max) await h.w.unmaximize()
      else await h.w.maximize()
      setIsMaximized(!max)
    }
  }
  const handleClose = async () => {
    const h = await win()
    if (h) await h.w.close()
  }

  useEffect(() => {
    let mounted = true
    ;(async () => {
      const h = await win()
      if (h && mounted) {
        try { setIsMaximized(await h.w.isMaximized()) } catch { /* noop */ }
      }
    })()
    return () => { mounted = false }
  }, [])

  return (
    <div
      data-tauri-drag-region
      className="h-10 bg-slate-900 text-white flex items-center justify-between px-4 select-none border-b border-slate-800 flex-shrink-0"
    >
      <div className="flex items-center gap-2 text-sm font-medium">
        <div className="w-6 h-6 bg-primary rounded-md flex items-center justify-center">
          <Factory className="w-3.5 h-3.5 text-white" strokeWidth={2.5} />
        </div>
        <span className="font-semibold">{APP_NAME}</span>
        {factory && (
          <>
            <span className="text-slate-500">—</span>
            <span className="text-slate-300">{factory.name}</span>
          </>
        )}
      </div>
      <div className="flex items-center gap-1" data-tauri-drag-region={undefined as unknown as undefined}>
        <button
          onClick={handleMinimize}
          className="w-9 h-9 flex items-center justify-center hover:bg-slate-800 rounded transition-colors"
          aria-label="Minimize"
        >
          <Minus className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={handleMaximize}
          className="w-9 h-9 flex items-center justify-center hover:bg-slate-800 rounded transition-colors"
          aria-label="Maximize"
        >
          {isMaximized ? <Square className="w-3 h-3" /> : <Maximize2 className="w-3.5 h-3.5" />}
        </button>
        <button
          onClick={handleClose}
          className="w-9 h-9 flex items-center justify-center hover:bg-red-600 rounded transition-colors"
          aria-label="Close"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}

export default TitleBar
