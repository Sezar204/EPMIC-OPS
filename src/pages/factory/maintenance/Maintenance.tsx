Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Wrench, Plus, Activity } from "lucide-react"
import { maintenanceApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { LineChart, BarChart } from "@/components/charts"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function Maintenance() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("schedule")
  const [wos, setWos]     = useState<any[]>([])
  const [bds, setBds]     = useState<any[]>([])
  const [assets, setAssets] = useState<any[]>([])
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    Promise.all([
      maintenanceApi.listWorkOrders(fid),
      maintenanceApi.listBreakdowns(fid),
      maintenanceApi.assets(fid),
      maintenanceApi.metrics(fid),
    ]).then(([w, b, a, m]) => {
      setWos((w.data as any[]) || [])
      setBds((b.data as any[]) || [])
      setAssets((a.data as any[]) || [])
      setMetrics(m.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { load() }, [fid])

  if (loading) return <PageSkeleton />

  const stats = {
    open:    wos.filter(w => !["completed", "cancelled"].includes(w.status)).length,
    inProg:  wos.filter(w => w.status === "in_progress").length,
    overdue: wos.filter(w => w.priority === "high" && !["completed", "cancelled"].includes(w.status)).length,
    doneMonth: wos.filter(w => w.status === "completed").length,
  }

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Maintenance</h1>
      <p className="text-sm text-slate-500 mb-6">Schedules, work orders, breakdowns, and asset health</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Open WOs" value={stats.open} color="primary" />
        <StatCard label="In Progress" value={stats.inProg} color="warning" />
        <StatCard label="High Priority" value={stats.overdue} color="danger" />
        <StatCard label="Completed" value={stats.doneMonth} color="success" />
      </div>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {["schedule", "wos", "breakdowns", "assets", "metrics"].map(t => (
            <Tabs.Trigger key={t} value={t}
              className={`px-4 py-2 text-sm font-medium border-b-2 capitalize ${tab === t ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t === "wos" ? "Work Orders" : t}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="schedule">
          <Card title="Preventive Maintenance Calendar" subtitle="Upcoming and overdue PMs">
            <p className="text-slate-500 text-sm py-6 text-center">Calendar view placeholder — click a date to schedule PM</p>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="wos">
          <Card padding="none" headerAction={<Button size="sm"><Plus className="w-3 h-3" /> New WO</Button>}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["WO #", "Machine", "Type", "Priority", "Status", "Assigned", "Downtime H"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {wos.length === 0 ? (
                    <tr><td colSpan={7} className="text-center py-12 text-slate-400 text-sm">No work orders</td></tr>
                  ) : wos.map(w => (
                    <tr key={w.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="px-3 py-2 font-mono text-xs">{w.wo_number}</td>
                      <td className="px-3 py-2">#{w.machine_id}</td>
                      <td className="px-3 py-2"><Badge variant="muted">{w.type}</Badge></td>
                      <td className="px-3 py-2"><Badge variant={w.priority === "high" || w.priority === "critical" ? "danger" : w.priority === "medium" ? "warning" : "muted"}>{w.priority}</Badge></td>
                      <td className="px-3 py-2"><Badge variant="muted">{w.status}</Badge></td>
                      <td className="px-3 py-2">{w.assigned_to ?? "—"}</td>
                      <td className="px-3 py-2 text-right">{w.downtime_hours}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="breakdowns">
          <Card padding="none">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["Machine", "Occurred", "Resolved", "Cause", "Description"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {bds.length === 0 ? (
                    <tr><td colSpan={5} className="text-center py-12 text-slate-400 text-sm">No breakdowns recorded</td></tr>
                  ) : bds.map(b => (
                    <tr key={b.id} className="border-b border-slate-100">
                      <td className="px-3 py-2">#{b.machine_id}</td>
                      <td className="px-3 py-2">{b.occurred_at?.slice(0, 16).replace("T", " ")}</td>
                      <td className="px-3 py-2">{b.resolved_at?.slice(0, 16).replace("T", " ") ?? "—"}</td>
                      <td className="px-3 py-2">{b.cause_category ?? "—"}</td>
                      <td className="px-3 py-2 text-xs">{b.description ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="assets">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {assets.map(a => (
              <Card key={a.machine_id} title={`${a.name}`} subtitle={a.code}>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between"><span className="text-slate-500">Status</span><Badge variant={a.status === "active" ? "success" : a.status === "down" ? "danger" : "warning"}>{a.status}</Badge></div>
                  <div className="flex justify-between"><span className="text-slate-500">Availability</span><span className="font-semibold">{a.availability_pct.toFixed(1)}%</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">MTBF</span><span>{a.mtbf_hours.toFixed(1)}h</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">MTTR</span><span>{a.mttr_hours.toFixed(1)}h</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Next PM</span><span>{a.next_pm_date ?? "—"}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Open WOs</span><span className="font-semibold">{a.open_work_orders}</span></div>
                </div>
              </Card>
            ))}
            {assets.length === 0 && <Card><div className="text-center py-8 text-slate-400 text-sm">No machines</div></Card>}
          </div>
        </Tabs.Content>

        <Tabs.Content value="metrics">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <StatCard label="Availability" value={`${metrics?.availability_pct?.toFixed(1) ?? 0}%`} color="success" />
            <StatCard label="Avg MTBF" value={`${metrics?.avg_mtbf_hours?.toFixed(1) ?? 0}h`} color="info" />
            <StatCard label="Avg MTTR" value={`${metrics?.avg_mttr_hours?.toFixed(1) ?? 0}h`} color="warning" />
            <StatCard label="PM Compliance" value={`${metrics?.pm_compliance_pct?.toFixed(1) ?? 0}%`} color="primary" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card title="Availability Trend">
              <LineChart
                data={(metrics?.availability_trend || []).map((d: any) => ({ date: d.date?.slice(5), Value: d.value }))}
                xKey="date" lines={[{ key: "Value", name: "Availability %", color: "#16A34A" }]} height={220}
              />
            </Card>
            <Card title="Breakdown Frequency by Machine">
              <BarChart
                data={(metrics?.breakdown_frequency || []).map((b: any) => ({ name: `M${b.machine_id}`, Count: b.count }))}
                xKey="name" bars={[{ key: "Count", name: "Breakdowns", color: "#DC2626" }]} height={220}
              />
            </Card>
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
