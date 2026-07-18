import {
  ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip,
  Legend, Bar, ReferenceLine, type TooltipProps,
} from "recharts"

interface BarSpec { key: string; name: string; color: string }
interface BarChartProps {
  data: Record<string, any>[]
  xKey: string
  bars: BarSpec[]
  height?: number
  referenceLine?: { y: number; label: string; color?: string }
}

export function BarChart({ data, xKey, bars, height = 300, referenceLine }: BarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
        <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: "#64748B" }} stroke="#CBD5E1" />
        <YAxis tick={{ fontSize: 12, fill: "#64748B" }} stroke="#CBD5E1" />
        <Tooltip content={<ChartTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {referenceLine && (
          <ReferenceLine y={referenceLine.y} stroke={referenceLine.color ?? "#DC2626"} strokeDasharray="4 4" label={referenceLine.label} />
        )}
        {bars.map((b) => (
          <Bar key={b.key} dataKey={b.key} name={b.name} fill={b.color} radius={[3, 3, 0, 0]} />
        ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  )
}

import { BarChart as RechartsBarChart } from "recharts"

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
