import { cn } from "@/utils/cn"

interface HealthGaugeProps {
  score: number
  size?: "sm" | "md" | "lg"
}

function colorFor(score: number) {
  if (score < 60) return "#DC2626"
  if (score < 75) return "#D97706"
  if (score < 90) return "#1E40AF"
  return "#16A34A"
}
function statusFor(score: number): string {
  if (score < 60) return "Critical"
  if (score < 75) return "Warning"
  if (score < 90) return "Good"
  return "Excellent"
}

export function HealthGauge({ score, size = "md" }: HealthGaugeProps) {
  const dims = { sm: 80, md: 120, lg: 180 }[size]
  const stroke = size === "sm" ? 7 : 10
  const r = (dims - stroke) / 2
  const c = 2 * Math.PI * r
  const pct = Math.max(0, Math.min(100, score)) / 100
  const color = colorFor(score)
  const fontSize = size === "sm" ? 18 : size === "md" ? 26 : 38

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: dims, height: dims }}>
      <svg width={dims} height={dims} className="-rotate-90">
        <circle cx={dims / 2} cy={dims / 2} r={r} fill="none" stroke="#E2E8F0" strokeWidth={stroke} />
        <circle
          cx={dims / 2}
          cy={dims / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - pct)}
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-bold text-slate-900" style={{ fontSize }}>{Math.round(score)}</span>
        {size !== "sm" && (
          <span className={cn("text-[11px] font-medium")} style={{ color }}>
            {statusFor(score)}
          </span>
        )}
      </div>
    </div>
  )
}
