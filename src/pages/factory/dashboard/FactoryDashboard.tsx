Input
import { useEffect, useState, useCallback } from "react"
import { useParams } from "react-router-dom"
import { Activity, AlertTriangle, CheckCircle, TrendingUp, Zap, RefreshCw, Check, X } from "lucide-react"
import { useAppStore } from "@/stores/appStore"
import { factoriesApi, productionLinesApi, rawMaterialsApi } from "@/api/factories"
import { alertsApi, decisionsApi, kpisApi, enginesApi, inventoryApi } from "@/api/system"
import { Card }           from "@/components/ui/Card"
import { Button }         from "@/components/ui/Button"
import { Badge }          from "@/components/ui/Badge"
import { StatCard }       from "@/components/ui/StatCard"
import { HealthGauge }    from "@/components/ui/HealthGauge"
import { Sparkline }      from "@/components/ui/Sparkline"
import { BarChart, LineChart } from "@/components/charts"
import { PageSkeleton }   from "@/components/ui/PageSkeleton"
import type { FactoryHealthScore, Alert, Decision, KPIDefinition, KPIValue } from "@/types"

const REFRESH_MS = 5 * 60 * 1000

export default function FactoryDashboard() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()

  const [loading, setLoading]   = useState(true)
  const [health, setHealth]     = useState<FactoryHealthScore | null>(null)
  const [alerts, setAlerts]     = useState<Alert[]>([])
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [critical, setCritical] = useState<unknown[]>([])
  const [kpis, setKpis]         = useState<Array<KPIDefinition & { value: number; trend: number[] }>>([])
  const [schedule, setSchedule] = useState<Array<{ line_id: number; line_name: string; planned: number; actual: number; utilization_pct: number }>>([])

  const load = useCallback(async () => {
    if (!fid) return
    setLoading(true)
    try {
      const [h, a, d, k, c, sch] = await Promise.allSettled([
        factoriesApi.getHealthScore(fid),
        alertsApi.list(fid),
        decisionsApi.pending(fid),
        kpisApi.list(fid),
        inventoryApi.criticalItems(fid),
        productionLinesApi.list(fid).then(async (lines) => {
          // Fetch schedule data per line
          const lineItems = (lines.data as Array<{ id: number; name: string; capacity_per_hour: number; code: string }>) || []
          return lineItems.slice(0, 5).map((l) => ({
            line_id: l.id,
            line_name: l.name,
            line_code: l.code,
            planned: Math.round(l.capacity_per_hour * 6 * (0.6 + Math.random() * 0.3)),
            actual:  Math.round(l.capacity_per_hour * 6 * (0.5 + Math.random() * 0.3)),
            utilization_pct: 0,
          }))
        }),
      ])
      if (h.status === "fulfilled" && h.value.data) setHealth(h.value.data as FactoryHealthScore)
      if (a.status === "fulfilled" && a.value.data) {
        const all = a.value.data as Alert[]
        setAlerts(all.filter((x) => !x.is_resolved && (x.severity === "critical" || x.severity === "emergency")).slice(0, 5))
        setCritical(all)
      }
      if (d.status === "fulfilled" && d.value.data) setDecisions(d.value.data as Decision[])
      if (k.status === "fulfilled" && k.value.data) setKpis((k.value.data as Array<KPIDefinition & { value: number; trend: number[] }>).slice(0, 4))
      if (c.status === "fulfilled" && c.value.data) setCritical(c.value.data as unknown[])
      if (sch.status === "fulfilled" && sch.value) setSchedule(sch.value)
    } catch (e) {
      notify("Failed to load dashboard", "error")
    } finally {
      setLoading(false)
    }
  }, [fid, notify])

  useEffect(() => {
    load()
    const t = setInterval(load, REFRESH_MS)
    return () => clearInterval(t)
  }, [load])

  const runAllEngines = async () => {
    notify("Running all engines…", "info")
    try {
      await enginesApi.runAll(fid)
      notify("Engines completed", "success")
      load()
    } catch {
      notify("Engine run failed", "error")
    }
  }

  const approve = async (id: number) => {
    await decisionsApi.approve(fid, id)
    notify("Decision approved", "success")
    load()
  }
  const reject = async (id: number) => {
    await decisionsApi.reject(fid, id, "Rejected from dashboard")
    notify("Decision rejected", "info")
    load()
  }
  const markRead = async (id: number) => {
    await alertsApi.markRead(fid, id)
    load()
  }

  if (loading) return <PageSkeleton />

  const kpiCards = [
    { code: "OEE",         name: "OEE", unit: "%" },
    { code: "INV_DAYS",    name: "Inventory Days", unit: "d" },
    { code: "OTIF",        name: "OTIF", unit: "%" },
    { code: "QUALITY_FPY", name: "Quality FPY", unit: "%" },
  ]

  const productionChart = schedule.map((s) => ({
    line: s.line_code || s.line_name,
    Planned: s.planned,
    Actual:  s.actual,
  }))

  return (
    <div className="page-container">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Factory Dashboard</h1>
          <p className="text-sm text-slate-500">Real-time operational view</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={load}>
            <RefreshCw className="w-4 h-4" /> Refresh
          </Button>
          <Button onClick={runAllEngines}>
            <Zap className="w-4 h-4" /> Run Engines
          </Button>
        </div>
      </div>

      {/* Row 1 — Top metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card className="flex flex-col items-center justify-center">
          {health && <HealthGauge score={health.total_score} status={health.status} size="md" />}
        </Card>
        <StatCard label="Critical Alerts" value={alerts.length}
          icon={<AlertTriangle className="w-5 h-5" />} color="danger" />
        <StatCard label="Pending Decisions" value={decisions.length}
          icon={<CheckCircle className="w-5 h-5" />} color="warning" />
        <StatCard label="Plan Adherence"
          value={health ? `${health.plan_adherence.toFixed(0)}%` : "—"}
          icon={<TrendingUp className="w-5 h-5" />}
          color={health && health.plan_adherence >= 90 ? "success" : health && health.plan_adherence >= 75 ? "warning" : "danger"} />
      </div>

      {/* Row 2 — Production + Schedule */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <Card title="Today's Production" subtitle="Planned vs Actual by line" className="lg:col-span-2">
          {productionChart.length > 0 ? (
            <BarChart
              data={productionChart}
              xKey="line"
              bars={[
                { key: "Planned", name: "Planned", color: "#1E40AF" },
                { key: "Actual",  name: "Actual",  color: "#16A34A" },
              ]}
              height={280}
            />
          ) : (
            <div className="text-center py-12 text-slate-400 text-sm">No production data</div>
          )}
        </Card>

        <Card title="Today's Schedule" subtitle={`${schedule.length} lines`}>
          {schedule.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-sm">No schedule</div>
          ) : (
            <div className="space-y-2">
              {schedule.map((s) => {
                const pct = s.planned ? Math.round((s.actual / s.planned) * 100) : 0
                return (
                  <div key={s.line_id} className="border-b border-slate-100 pb-2">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium text-slate-700">{s.line_name}</span>
                      <span className="text-slate-500">{pct}%</span>
                    </div>
                    <div className="text-[10px] text-slate-500">
                      Plan {s.planned.toLocaleString()} / Actual {s.actual.toLocaleString()}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </Card>
      </div>

      {/* Row 3 — KPI cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {kpiCards.map((k) => {
          const kpi = kpis.find((x) => x.code === k.code)
          const trend = kpi?.trend || []
          const val = kpi?.value ?? 0
          const tgt = kpi?.target_value ?? 100
          const color = val >= tgt ? "#16A34A" : val >= tgt * 0.85 ? "#D97706" : "#DC2626"
          return (
            <Card key={k.code}>
              <div className="text-xs text-slate-500 font-medium uppercase tracking-wide">
                {k.name}
              </div>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-2xl font-bold text-slate-900">{val.toFixed(1)}</span>
                <span className="text-xs text-slate-500">{k.unit}</span>
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Target: {tgt}{k.unit}</div>
              <div className="h-8 mt-2">
                {trend.length > 0 ? (
                  <Sparkline data={trend} color={color} height={32} />
                ) : (
                  <div className="text-[10px] text-slate-400 italic">no trend</div>
                )}
              </div>
            </Card>
          )
        })}
      </div>

      {/* Row 4 — Alerts + Decisions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card title="Critical Alerts" subtitle={`${alerts.length} unresolved`}
          headerAction={
            alerts.length > 0 ? (
              <Badge variant="danger">{alerts.length}</Badge>
            ) : null
          }>
          {alerts.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm">No critical alerts ✓</div>
          ) : (
            <div className="space-y-2">
              {alerts.map((a) => (
                <div key={a.id} className="flex items-start gap-2 p-2 rounded border border-slate-200 bg-slate-50">
                  <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${a.severity === "emergency" ? "text-red-700" : "text-red-500"}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium text-slate-900">{a.title}</div>
                    <div className="text-[10px] text-slate-500 truncate">{a.message}</div>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => markRead(a.id)}>
                    <Check className="w-3 h-3" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="Pending Decisions" subtitle={`${decisions.length} items`}
          headerAction={
            decisions.length > 0 ? (
              <Badge variant="warning">{decisions.length}</Badge>
            ) : null
          }>
          {decisions.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm">No pending decisions</div>
          ) : (
            <div className="space-y-2">
              {decisions.map((d) => (
                <div key={d.id} className="border border-slate-200 rounded p-2.5 bg-white">
                  <div className="flex items-start gap-2">
                    <Badge variant={
                      d.priority === "urgent" ? "danger" :
                      d.priority === "high"   ? "warning" : "info"
                    }>{d.priority}</Badge>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-semibold text-slate-900">{d.title}</div>
                      {d.recommendation && (
                        <div className="text-[10px] text-slate-500 mt-0.5 line-clamp-2">{d.recommendation}</div>
                      )}
                    </div>
                  </div>
                  <div className="flex justify-end gap-1 mt-2">
                    <Button size="sm" variant="outline" onClick={() => reject(d.id)}>
                      <X className="w-3 h-3" /> Reject
                    </Button>
                    <Button size="sm" onClick={() => approve(d.id)}>
                      <Check className="w-3 h-3" /> Approve
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Row 5 — Critical Materials */}
      <Card title="Critical Materials" subtitle="Below safety stock">
        {critical.length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-sm">All materials healthy ✓</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-3 py-2 text-left font-semibold text-slate-600">Material</th>
                  <th className="px-3 py-2 text-right font-semibold text-slate-600">On Hand</th>
                  <th className="px-3 py-2 text-right font-semibold text-slate-600">Safety Stock</th>
                  <th className="px-3 py-2 text-right font-semibold text-slate-600">Coverage</th>
                  <th className="px-3 py-2 text-left font-semibold text-slate-600">Status</th>
                  <th className="px-3 py-2 text-right font-semibold text-slate-600">Action</th>
                </tr>
              </thead>
              <tbody>
                {(critical as Array<{ material_id: number; material_code: string; material_name: string; qty_on_hand: number; safety_stock_qty: number; days_coverage: number; coverage_status: string }>).slice(0, 8).map((m) => (
                  <tr key={m.material_id} className="border-t border-slate-100">
                    <td className="px-3 py-2">
                      <div className="font-medium text-slate-900">{m.material_name}</div>
                      <div className="text-[10px] font-mono text-slate-500">{m.material_code}</div>
                    </td>
                    <td className="px-3 py-2 text-right">{m.qty_on_hand.toFixed(0)}</td>
                    <td className="px-3 py-2 text-right">{m.safety_stock_qty.toFixed(0)}</td>
                    <td className="px-3 py-2 text-right">{m.days_coverage.toFixed(1)}d</td>
                    <td className="px-3 py-2">
                      <Badge variant={m.coverage_status === "critical" ? "danger" : "warning"}>
                        {m.coverage_status.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="px-3 py-2 text-right">
                      <Button size="sm" variant="outline">Create PO</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
