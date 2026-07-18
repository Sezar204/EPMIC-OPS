import { useEffect, useRef, useState } from "react"
import { Factory } from "lucide-react"

interface Props {
  onReady: () => void
}

const STEPS = [
  { label: "Starting services...",         ms: 800 },
  { label: "Connecting to database...",    ms: 600 },
  { label: "Checking data integrity...",   ms: 500 },
  { label: "Loading workspace...",         ms: 400 },
  { label: "Ready.",                       ms: 300 },
]

export function SplashScreen({ onReady }: Props) {
  const [stepIdx, setStepIdx] = useState(0)
  const [progress, setProgress] = useState(0)
  const doneRef = useRef(false)

  useEffect(() => {
    let alive = true
    const totalMs = STEPS.reduce((a, s) => a + s.ms, 0)
    const t0 = Date.now()

    const tick = () => {
      if (!alive) return
      const elapsed = Date.now() - t0
      const p = Math.min(100, Math.round((elapsed / totalMs) * 100))
      setProgress(p)

      let acc = 0
      let idx = 0
      for (let i = 0; i < STEPS.length; i++) {
        acc += STEPS[i].ms
        if (elapsed < acc) { idx = i; break }
        idx = i
      }
      setStepIdx(idx)

      if (elapsed >= totalMs && !doneRef.current) {
        doneRef.current = true
        setProgress(100)
        setTimeout(() => { if (alive) onReady() }, 400)
        return
      }
      requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
    return () => { alive = false }
  }, [onReady])

  return (
    <div className="fixed inset-0 bg-slate-900 flex flex-col items-center justify-center">
      <div className="flex flex-col items-center">
        <div className="w-20 h-20 rounded-2xl bg-primary flex items-center justify-center shadow-lg shadow-blue-900/40">
          <Factory className="w-10 h-10 text-white" />
        </div>
        <h1 className="mt-6 text-4xl font-bold text-white tracking-tight">EMICP</h1>
        <p className="mt-2 text-sm text-slate-400">
          One Platform. All Factories. One Decision.
        </p>
      </div>

      <div className="mt-10 w-72">
        <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-150 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className={`mt-3 text-xs text-center ${stepIdx >= STEPS.length - 1 ? "text-green-400" : "text-slate-500"}`}>
          {STEPS[stepIdx].label}
        </p>
      </div>

      <span className="absolute bottom-4 right-4 text-xs text-slate-600">v1.0.0</span>
    </div>
  )
}
