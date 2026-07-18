Input
import { cn } from "@/utils/cn"

interface Props {
  score: number
  size?: "sm" | "md" | "lg"
  status?: "excellent" | "good" | "warning" | "critical"
}

const SIZE = {
  sm: { px: 100, stroke: 8,   font: "text-lg"  },
  md: { px: 140, stroke: 10,  font: "text-2xl" },
  lg: { px: 180, stroke: 12,  font: "text-3xl" },
}

function colorFor(score: number) {
  if (score >= 90) return { stroke: "#16A34A", label: "Excellent", bg: "bg-green-100",  text: "text-green-700" }
  if (score >= 75) return { stroke: "#1E40AF", label: "Good",      bg: "bg-blue-100",   text: "text-blue-700" }
  if (score >= 60) return { stroke: "#D97706", label: "Warning",   bg: "bg-yellow-100", text: "text-yellow-700" }
  return            { stroke: "#DC2626", label: "Critical",   bg: "bg-red-100",    text: "text-red-700" }
}

export function HealthGauge({ score, size = "md", status }: Props) {
  const { px, stroke, font } = SIZE[size]
  const c = colorFor(score)
  const radius = (px - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference
  const finalStatus = status || (score >= 90 ? "excellent" : score >= 75 ? "good" : score >= 60 ? "warning" : "critical")

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: px, height: px }}>
        <svg width={px} height={px} className="-rotate-90">
          <circle
            cx={px / 2} cy={px / 2} r={radius}
            fill="none" stroke="#F1F5F9" strokeWidth={stroke}
          />
          <circle
            cx={px / 2} cy={px / 2} r={radius}
            fill="none"
            stroke={c.stroke}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.6s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className={cn("font-bold", font, c.text)}>{Math.round(score)}</div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">/ 100</div>
        </div>
      </div>
      <div className={cn("text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded", c.bg, c.text)}>
        {finalStatus}
      </div>
    </div>
  )
}

export default HealthGauge
