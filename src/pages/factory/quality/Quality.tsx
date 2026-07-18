Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { CheckCircle, AlertTriangle, Plus, FileWarning, Wrench } from "lucide-react"
import { qualityApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { LineChart, BarChart } from "@/components/charts"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function Quality() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("inspections")
  const [checks, setChecks] = useState<any[]>([])
  const [ncrs, setNcrs]   = useState<any[]>([])
  const [capas, setCapas] = useState<any[]>([])
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    Promise.all([
      qualityApi.listChecks(fid),
      qualityApi.listNCR(fid),
      qualityApi.listCAPA(fid),
      qualityApi.metrics(fid),
    ]).then(([c, n, ca, m]) => {
      setChecks((c.data as any[]) || [])
      setNcrs((n.data as any[]) || [])
      setCapas((ca.data as any[]) || [])
      setMetrics(m.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { load() }, [fid])

  if (loading) return <PageSkeleton />

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Quality</h1>
      <p className="text-sm text-slate-500 mb-6">Inspections, NCRs, CAPAs, and metrics</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Defect Rate" value={`${metrics?.defect_rate_pct?.toFixed(1) ?? 0}%`} color="danger" />
        <StatCard label="First Pass Yield" value={`${metrics?.first_pass_yield_pct?.toFixed(1) ?? 0}%`} color="success" />
        <StatCard label="CAPA Closure" value={`${metrics?.capa_closure_rate_pct?.toFixed(1) ?? 0}%`} color="info" />
        <StatCard label="Supplier Quality" value={`${metrics?.supplier_quality_pct?.toFixed(1) ?? 0}%`} color="primary" />
      </div>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {[{v: "inspections", l: "Inspections"}, {v: "ncr", l: "NCR"}, {v: "capa", l: "CAPA"}, {v: "metrics", l: "Metrics"}].map(t => (
            <Tabs.Trigger key={t.v} value={t.v}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${tab === t.v ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t.l}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="inspections">
          <Card padding="none" headerAction={<Button size="sm"><Plus className="w-3 h-3" /> New</Button>}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["Date", "Type", "Sample", "Defects", "Defect %", "Status", "Decision"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {checks.length === 0 ? (
                    <tr><td colSpan={7} className="text-center py-12 text-slate-400 text-sm">No inspections</td></tr>
                  ) : checks.map(c => (
                    <tr key={c.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="px-3 py-2">{c.checked_at?.slice(0, 10) ?? "—"}</td>
                      <td className="px-3 py-2"><Badge variant="muted">{c.check_type?.toUpperCase()}</Badge></td>
                      <td className="px-3 py-2 text-right">{c.sample_size}</td>
                      <td className="px-3 py-2 text-right">{c.defects_found}</td>
                      <td className="px-3 py-2 text-right">{c.defect_rate_pct?.toFixed(1)}%</td>
                      <td className="px-3 py-2"><Badge variant={c.status === "passed" ? "success" : c.status === "failed" ? "danger" : "warning"}>{c.status}</Badge></td>
                      <td className="px-3 py-2">{c.decision ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="ncr">
          <Card padding="none" headerAction={<Button size="sm"><Plus className="w-3 h-3" /> New NCR</Button>}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["NCR #", "Title", "Severity", "Status", "Opened", "Closed"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {ncrs.length === 0 ? (
                    <tr><td colSpan={6} className="text-center py-12 text-slate-400 text-sm">No NCRs</td></tr>
                  ) : ncrs.map(n => (
                    <tr key={n.id} className="border-b border-slate-100">
                      <td className="px-3 py-2 font-mono text-xs">{n.ncr_number}</td>
                      <td className="px-3 py-2">{n.title}</td>
                      <td className="px-3 py-2"><Badge variant={n.severity === "high" ? "danger" : "warning"}>{n.severity}</Badge></td>
                      <td className="px-3 py-2"><Badge variant="muted">{n.status}</Badge></td>
                      <td className="px-3 py-2">{n.created_at?.slice(0, 10)}</td>
                      <td className="px-3 py-2">{n.closed_at?.slice(0, 10) ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="capa">
          <Card padding="none" headerAction={<Button size="sm"><Plus className="w-3 h-3" /> New CAPA</Button>}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["CAPA #", "Type", "Description", "Responsible", "Due", "Status"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {capas.length === 0 ? (
                    <tr><td colSpan={6} className="text-center py-12 text-slate-400 text-sm">No CAPAs</td></tr>
                  ) : capas.map(c => {
                    const overdue = c.due_date && new Date(c.due_date) < new Date() && c.status !== "closed"
                    return (
                      <tr key={c.id} className={`border-b border-slate-100 ${overdue ? "bg-red-50" : ""}`}>
                        <td className="px-3 py-2 font-mono text-xs">{c.capa_number}</td>
                        <td className="px-3 py-2"><Badge variant="muted">{c.type}</Badge></td>
                        <td className="px-3 py-2 max-w-xs truncate">{c.description}</td>
                        <td className="px-3 py-2">{c.responsible_person ?? "—"}</td>
                        <td className="px-3 py-2">{c.due_date?.slice(0, 10) ?? "—"}</td>
                        <td className="px-3 py-2"><Badge variant={c.status === "closed" ? "success" : "warning"}>{c.status}</Badge></td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="metrics">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card title="Weekly Defect Trend">
              <LineChart
                data={(metrics?.weekly_defect_trend || []).map((w: any) => ({ period: w.period, Rate: w.value }))}
                xKey="period"
                lines={[{ key: "Rate", name: "Defect Rate %", color: "#DC2626" }]}
                height={220}
              />
            </Card>
            <Card title="Top Defect Categories">
              <BarChart
                data={(metrics?.top_defect_categories || []).map((c: any) => ({ name: c.category, Count: c.count }))}
                xKey="name"
                bars={[{ key: "Count", name: "Count", color: "#1E40AF" }]}
                height={220}
              />
            </Card>
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
