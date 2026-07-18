import {
  ResponsiveContainer, PieChart as RechartsPie, Pie, Cell,
  Tooltip, Legend, type TooltipProps,
} from "recharts"

interface PieDatum { name: string; value: number; color: string }
interface PieChartProps {
  data: PieDatum[]
  height?: number
}

export function PieChart({ data, height = 300 }: PieChartProps) {
  const total = data.reduce((a, d) => a + d.value, 0)
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsPie>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={2}
          isAnimationActive={false}
        >
          {data.map((d, i) => (
            <Cell key={i} fill={d.color} />
          ))}
        </Pie>
        <Tooltip content={<ChartTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <text x="50%" y="46%" textAnchor="middle" dominantBaseline="middle" className="fill-slate-900 text-2xl font-bold">
          {total}
        </text>
        <text x="50%" y="56%" textAnchor="middle" dominantBaseline="middle" className="fill-slate-400 text-xs">
          Total
        </text>
      </RechartsPie>
    </ResponsiveContainer>
  )
}

function ChartTooltip({ active, payload }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null
  const p = payload[0]
  return (
    <div className="bg-white border border-border rounded-lg shadow-md p-2 text-xs">
      <p className="font-semibold text-slate-800">{p.name}</p>
      <p className="text-slate-600">Value: <span className="font-medium text-slate-900">{p.value}</span></p>
    </div>
  )
}
