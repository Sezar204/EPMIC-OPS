Input
import { useEffect, useState } from "react"
import { Factory } from "lucide-react"
import { APP_NAME, APP_VERSION, APP_TAGLINE } from "@/constants"

interface Props { onReady: () => void }

const STEPS = [
  { text: "Starting services...",      ms: 800 },
  { text: "Connecting to database...", ms: 600 },
  { text: "Checking data integrity...",ms: 500 },
  { text: "Loading workspace...",      ms: 400 },
  { text: "Ready.",                    ms: 300 },
]

export function SplashScreen({ onReady }: Props) {
  const [stepIndex, setStepIndex]   = useState(0)
  const [progress, setProgress]     = useState(0)
  const [done, setDone]             = useState(false)

  useEffect(() => {
    if (stepIndex >= STEPS.length) {
      setDone(true)
      const t = setTimeout(() => onReady(), 400)
      return () => clearTimeout(t)
    }
    const total = STEPS.reduce((a, s) => a + s.ms, 0)
    let elapsed = 0
    for (let i = 0; i < stepIndex; i++) elapsed += STEPS[i].ms
    elapsed += STEPS[stepIndex].ms
    setProgress(Math.min(100, (elapsed / total) * 100))

    const t = setTimeout(() => setStepIndex((i) => i + 1), STEPS[stepIndex].ms)
    return () => clearTimeout(t)
  }, [stepIndex, onReady])

  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-slate-900 text-white">
      <div className="flex flex-col items-center gap-6 animate-fade-in">
        <div className="w-20 h-20 bg-primary rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30">
          <Factory className="w-10 h-10 text-white" strokeWidth={1.5} />
        </div>
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">{APP_NAME}</h1>
          <p className="text-sm text-slate-400 mt-1">{APP_TAGLINE}</p>
        </div>
        <div className="w-72">
          <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        <p className={`text-sm font-mono ${done ? "text-green-400" : "text-slate-400"}`}>
          {done ? "Ready." : STEPS[Math.min(stepIndex, STEPS.length - 1)].text}
        </p>
      </div>
      <div className="absolute bottom-4 right-4 text-xs text-slate-500 font-mono">
        v{APP_VERSION}
      </div>
    </div>
  )
}
