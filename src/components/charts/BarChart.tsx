Input
import {
  BarChart as RBarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine,
} from "recharts"

export interface BarSeries {
  key: string
  name: string
  color: string
}

interface Props {
  data: Array<Record<string, string | number>>
  xKey: string
  bars: BarSeries[]
  height?: number
  referenceValue?: number
  referenceLabel?: string
  yLabel?: string
}

export function BarChart({
  data, xKey, bars, height = 300, referenceValue, referenceLabel, yLabel,
}: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RBarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: "#64748B" }} />
        <YAxis tick={{ fontSize: 11, fill: "#64748B" }} label={
          yLabel ? { value: yLabel, angle: -90, position: "insideLeft", style: { fontSize: 11, fill: "#64748B" } } : undefined
        } />
        <Tooltip
          contentStyle={{ backgroundColor: "#0F172A", border: "none", borderRadius: 6, fontSize: 12, color: "#fff" }}
          cursor={{ fill: "#F1F5F9" }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {referenceValue !== undefined && (
          <ReferenceLine y={referenceValue} stroke="#1E40AF" strokeDasharray="3 3"
            label={referenceLabel ? { value: referenceLabel, position: "right", fontSize: 10, fill: "#1E40AF" } : undefined}
          />
        )}
        {bars.map((b) => (
          <Bar key={b.key} dataKey={b.key} name={b.name} fill={b.color} radius={[4, 4, 0, 0]} />
        ))}
      </RBarChart>
    </ResponsiveContainer>
  )
}

export default BarChart
