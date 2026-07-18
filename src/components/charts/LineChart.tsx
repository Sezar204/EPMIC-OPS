import {
  ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip,
  Legend, Line, type TooltipProps,
} from "recharts"

interface LineSpec { key: string; name: string; color: string; dashed?: boolean }
interface LineChartProps {
  data: Record<string, any>[]
  xKey: string
  lines: LineSpec[]
  height?: number
}

export function LineChart({ data, xKey, lines, height = 300 }: LineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
        <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: "#64748B" }} stroke="#CBD5E1" />
        <YAxis tick={{ fontSize: 12, fill: "#64748B" }} stroke="#CBD5E1" />
        <Tooltip content={<ChartTooltip />} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {lines.map((l) => (
          <Line
            key={l.key}
            type="monotone"
            dataKey={l.key}
            name={l.name}
            stroke={l.color}
            strokeWidth={2}
            strokeDasharray={l.dashed ? "5 4" : undefined}
            dot={{ r: 2 }}
            isAnimationActive={false}
          />
        ))}
      </RechartsLineChart>
    </ResponsiveContainer>
  )
}

import { LineChart as RechartsLineChart } from "recharts"

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
