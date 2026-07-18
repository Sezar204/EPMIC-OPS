import {
  ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip,
  Legend, Area, type TooltipProps,
} from "recharts"

interface AreaSpec { key: string; name: string; color: string }
interface AreaChartProps {
  data: Record<string, any>[]
  xKey: string
  areas: AreaSpec[]
  height?: number
}

export function AreaChartComp({ data, xKey, areas, height = 300 }: AreaChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsAreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
        <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: "#64748B" }} stroke="#CBD5E1" />
        <YAxis tick={{ fontSize: 12, fill: "#64748B" }} stroke="#CBD5E1" />
        <Tooltip content={<ChartTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {areas.map((a) => (
          <Area
            key={a.key}
            type="monotone"
            dataKey={a.key}
            name={a.name}
            stroke={a.color}
            fill={a.color}
            fillOpacity={0.3}
            isAnimationActive={false}
          />
        ))}
      </RechartsAreaChart>
    </ResponsiveContainer>
  )
}

import { AreaChart as RechartsAreaChart } from "recharts"

function ChartTooltip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-border rounded-lg shadow-md p-2 text-xs">
      <p className="font-semibold text-slate-800 mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey as string} className="text-slate-600">
          {p.name}: <span className="font-medium text-slate-900">{p.value}</span>
        </p>
      ))}
    </div>
  )
}

export { AreaChartComp as AreaChart }
