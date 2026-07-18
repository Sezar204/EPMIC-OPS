import { useEffect, useState } from "react"
import { Factory, Minus, Square, X } from "lucide-react"
import { useAppStore } from "@/stores/appStore"

export function TitleBar() {
  const currentFactory = useAppStore((s) => s.currentFactory)
  const [windowApi, setWindowApi] = useState<any>(null)

  useEffect(() => {
    (async () => {
      try {
        const mod = await import("@tauri-apps/api/window")
        setWindowApi(mod.getCurrentWindow())
      } catch {
        // Browser dev mode — window API unavailable, controls hidden via no-op handlers
      }
    })()
  }, [])

  const minimize = async () => { try { await windowApi?.minimize() } catch {} }
  const toggleMax = async () => { try { await windowApi?.toggleMaximize() } catch {} }
  const close = async () => { try { await windowApi?.close() } catch {} }

  return (
    <div
      data-tauri-drag-region
      className="h-10 flex items-center justify-between bg-secondary px-3 border-b border-slate-800 select-none shrink-0"
    >
      <div className="flex items-center gap-2" data-tauri-drag-region>
        <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
          <Factory className="w-3.5 h-3.5 text-white" />
        </div>
        <span className="text-white font-semibold text-sm">EMICP</span>
        {currentFactory && (
          <>
            <span className="text-slate-500">—</span>
            <span className="text-slate-300 text-sm">{currentFactory.name}</span>
          </>
        )}
      </div>

      <div className="flex items-center">
        <button
          onClick={minimize}
          className="w-10 h-10 flex items-center justify-center text-slate-400 hover:bg-slate-800 hover:text-white transition"
          title="Minimize"
        >
          <Minus className="w-4 h-4" />
        </button>
        <button
          onClick={toggleMax}
          className="w-10 h-10 flex items-center justify-center text-slate-400 hover:bg-slate-800 hover:text-white transition"
          title="Maximize"
        >
          <Square className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={close}
          className="w-10 h-10 flex items-center justify-center text-slate-400 hover:bg-danger hover:text-white transition"
          title="Close"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
