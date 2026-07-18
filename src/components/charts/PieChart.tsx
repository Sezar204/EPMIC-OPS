Input
import { PieChart as RPieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts"

export interface PieSlice {
  name: string
  value: number
  color: string
}

interface Props {
  data: PieSlice[]
  height?: number
  showCenterTotal?: boolean
}

export function PieChart({ data, height = 300, showCenterTotal = true }: Props) {
  const total = data.reduce((a, d) => a + d.value, 0)
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={showCenterTotal ? 60 : 0}
          outerRadius={90}
          paddingAngle={2}
          dataKey="value"
          label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
          labelLine={false}
        >
          {data.map((entry, i) => (
            <Cell key={`c-${i}`} fill={entry.color} />
          ))}
        </Pie>
        {showCenterTotal && (
          <text
            x="50%"
            y="50%"
            textAnchor="middle"
            dominantBaseline="middle"
            className="fill-slate-900"
          >
            <tspan x="50%" dy="-0.4em" fontSize="11" fill="#64748B">Total</tspan>
            <tspan x="50%" dy="1.4em" fontSize="20" fontWeight="700" fill="#0F172A">
              {total.toLocaleString()}
            </tspan>
          </text>
        )}
        <Tooltip
          contentStyle={{ backgroundColor: "#0F172A", border: "none", borderRadius: 6, fontSize: 12, color: "#fff" }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
      </RPieChart>
    </ResponsiveContainer>
  )
}

export default PieChart
