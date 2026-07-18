Input
import {
  AreaChart as RAreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer,
} from "recharts"

export interface AreaSeries {
  key: string
  name: string
  color: string
}

interface Props {
  data: Array<Record<string, string | number>>
  xKey: string
  areas: AreaSeries[]
  height?: number
  stacked?: boolean
}

export function AreaChart({ data, xKey, areas, height = 300, stacked = false }: Props) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RAreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          {areas.map((a) => (
            <linearGradient key={a.key} id={`grad-${a.key}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"  stopColor={a.color} stopOpacity={0.4} />
              <stop offset="100%" stopColor={a.color} stopOpacity={0.05} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: "#64748B" }} />
        <YAxis tick={{ fontSize: 11, fill: "#64748B" }} />
        <Tooltip
          contentStyle={{ backgroundColor: "#0F172A", border: "none", borderRadius: 6, fontSize: 12, color: "#fff" }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {areas.map((a) => (
          <Area
            key={a.key}
            type="monotone"
            dataKey={a.key}
            name={a.name}
            stroke={a.color}
            strokeWidth={2}
            fill={`url(#grad-${a.key})`}
            stackId={stacked ? "1" : undefined}
          />
        ))}
      </RAreaChart>
    </ResponsiveContainer>
  )
}

export default AreaChart
