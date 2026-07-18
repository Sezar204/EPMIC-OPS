Input
import { LineChart, Line, ResponsiveContainer, YAxis } from "recharts"

interface Props {
  data: number[]
  color?: string
  width?: number
  height?: number
}

export function Sparkline({
  data,
  color = "#1E40AF",
  width,
  height = 32,
}: Props) {
  const chartData = data.map((v, i) => ({ i, v }))
  const min = Math.min(...data)
  const max = Math.max(...data)
  const pad = (max - min) * 0.15 || 1
  const yMin = min - pad
  const yMax = max + pad

  if (data.length === 0) {
    return <div className="text-[10px] text-slate-400 italic">no data</div>
  }

  return (
    <div style={{ width: width ?? "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
          <YAxis hide domain={[yMin, yMax]} />
          <Line
            type="monotone"
            dataKey="v"
            stroke={color}
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default Sparkline
