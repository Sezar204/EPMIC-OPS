Input
import {
  LineChart as RLineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer,
} from "recharts"

export interface LineSeries {
  key: string
  name: string
  color: string
  dashed?: boolean
}

interface Props {
  data: Array<Record<string, string | number>>
  xKey: string
  lines: LineSeries[]
  height?: number
  yLabel?: string
}

export function LineChart({ data, xKey, lines, height = 300, yLabel }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RLineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: "#64748B" }} />
        <YAxis tick={{ fontSize: 11, fill: "#64748B" }} label={
          yLabel ? { value: yLabel, angle: -90, position: "insideLeft", style: { fontSize: 11, fill: "#64748B" } } : undefined
        } />
        <Tooltip
          contentStyle={{ backgroundColor: "#0F172A", border: "none", borderRadius: 6, fontSize: 12, color: "#fff" }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {lines.map((l) => (
          <Line
            key={l.key}
            type="monotone"
            dataKey={l.key}
            name={l.name}
            stroke={l.color}
            strokeWidth={2}
            strokeDasharray={l.dashed ? "5 5" : undefined}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        ))}
      </RLineChart>
    </ResponsiveContainer>
  )
}

export default LineChart
