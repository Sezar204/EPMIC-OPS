Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Calendar, Plus, RefreshCw } from "lucide-react"
import { productionApi, productionLinesApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { BarChart } from "@/components/charts"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function ProductionPlanning() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("daily")
  const [schedule, setSchedule] = useState<any[]>([])
  const [orders, setOrders] = useState<any[]>([])
  const [lines, setLines] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const today = new Date().toISOString().slice(0, 10)

  useEffect(() => {
    Promise.all([
      productionApi.dailySchedule(fid, today),
      productionApi.listOrders(fid),
      productionLinesApi.list(fid),
    ]).then(([s, o, l]) => {
      setSchedule((s.data as any[]) || [])
      setOrders((o.data as any[]) || [])
      setLines((l.data as any[]) || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [fid, today])

  if (loading) return <PageSkeleton />

  const lineMap: Record<number, any> = {}
  lines.forEach(l => { lineMap[l.id] = l })

  return (
    <div className="page-container">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Production Planning</h1>
          <p className="text-sm text-slate-500">Daily, weekly, and monthly schedule</p>
        </div>
        <Button><Plus className="w-4 h-4" /> Generate Plan</Button>
      </div>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {["daily", "weekly", "monthly"].map(t => (
            <Tabs.Trigger key={t} value={t}
              className={`px-4 py-2 text-sm font-medium border-b-2 capitalize ${tab === t ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="daily">
          <Card title={`Schedule — ${today}`} subtitle="Gantt by line">
            {schedule.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-sm">No schedule for today</div>
            ) : (
              <div className="space-y-2">
                {schedule.map(s => (
                  <div key={s.line_id} className="border border-slate-200 rounded p-2">
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="text-sm font-semibold">{s.line_name} <span className="text-xs text-slate-500 font-mono">({s.line_code})</span></div>
                      <Badge variant={s.utilization_pct > 90 ? "danger" : s.utilization_pct > 80 ? "warning" : "success"}>
                        {s.utilization_pct.toFixed(0)}% util
                      </Badge>
                    </div>
                    <div className="flex gap-1 min-h-[40px] bg-slate-50 rounded p-1">
                      {(s.blocks || []).map((b: any) => (
                        <div key={b.order_id}
                          className={`flex-1 p-1.5 rounded text-[10px] text-white font-medium ${
                            b.status === "completed"   ? "bg-slate-400" :
                            b.status === "in_progress" ? "bg-green-500" :
                            b.status === "planned"     ? "bg-blue-500" : "bg-red-500"
                          }`}>
                          <div className="truncate">{b.order_number}</div>
                          <div className="text-[9px] opacity-80">{b.actual}/{b.planned}</div>
                        </div>
                      ))}
                      {s.blocks?.length === 0 && <div className="flex-1 flex items-center justify-center text-slate-400 text-xs">No orders</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </Tabs.Content>

        <Tabs.Content value="weekly">
          <Card title="Weekly View" subtitle="Coming soon">
            <p className="text-sm text-slate-500 py-6 text-center">Weekly grid view placeholder</p>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="monthly">
          <Card title="Monthly View" subtitle="Coming soon">
            <p className="text-sm text-slate-500 py-6 text-center">Monthly capacity planning placeholder</p>
          </Card>
        </Tabs.Content>
      </Tabs.Root>

      <Card title="Production Orders" className="mt-4" padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                {["Order #", "Product", "Line", "Plan", "Actual", "Status", "Adherence %"].map(h => (
                  <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {orders.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-12 text-slate-400 text-sm">No production orders</td></tr>
              ) : orders.map(o => {
                const pct = o.planned_qty ? Math.round((o.actual_qty / o.planned_qty) * 100) : 0
                return (
                  <tr key={o.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="px-3 py-2 font-mono text-xs">{o.order_number}</td>
                    <td className="px-3 py-2">#{o.product_id}</td>
                    <td className="px-3 py-2">{lineMap[o.line_id]?.name ?? "—"}</td>
                    <td className="px-3 py-2 text-right">{o.planned_qty}</td>
                    <td className="px-3 py-2 text-right">{o.actual_qty}</td>
                    <td className="px-3 py-2"><Badge variant="muted">{o.status}</Badge></td>
                    <td className="px-3 py-2">
                      <span className={pct >= 95 ? "text-green-600 font-semibold" : pct >= 80 ? "text-yellow-600" : "text-red-600 font-semibold"}>
                        {pct}%
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
