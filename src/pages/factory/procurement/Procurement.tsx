Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { ShoppingCart, RefreshCw, Plus, CheckCircle } from "lucide-react"
import { procurementApi, suppliersApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { LineChart } from "@/components/charts"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function Procurement() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("pos")
  const [pos, setPos] = useState<any[]>([])
  const [reqs, setReqs] = useState<any[]>([])
  const [perf, setPerf] = useState<any[]>([])
  const [suppliers, setSuppliers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    Promise.all([
      procurementApi.listPOs(fid),
      procurementApi.requirements(fid),
      procurementApi.supplierPerf(fid),
      suppliersApi.list(fid),
    ]).then(([p, r, s, sup]) => {
      setPos((p.data as any[]) || [])
      setReqs((r.data as any[]) || [])
      setPerf((s.data as any[]) || [])
      setSuppliers((sup.data as any[]) || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { load() }, [fid])

  if (loading) return <PageSkeleton />

  const stats = {
    open: pos.filter(p => !["received", "closed", "cancelled"].includes(p.status)).length,
    total: pos.reduce((a, p) => a + (p.total_value || 0), 0),
    overdue: pos.filter(p => p.expected_delivery && new Date(p.expected_delivery) < new Date() && !["received", "closed"].includes(p.status)).length,
    dueWeek: pos.filter(p => {
      if (!p.expected_delivery) return false
      const days = (new Date(p.expected_delivery).getTime() - Date.now()) / 86400000
      return days >= 0 && days <= 7 && !["received", "closed"].includes(p.status)
    }).length,
  }

  const supplierMap: Record<number, string> = {}
  suppliers.forEach(s => { supplierMap[s.id] = s.name })

  return (
    <div className="page-container">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Procurement</h1>
          <p className="text-sm text-slate-500">Purchase orders, requirements, and supplier performance</p>
        </div>
        <Button><Plus className="w-4 h-4" /> New PO</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Open POs" value={stats.open} color="primary" />
        <StatCard label="Total Value" value={`$${stats.total.toLocaleString()}`} color="info" />
        <StatCard label="Overdue" value={stats.overdue} color="danger" />
        <StatCard label="Due This Week" value={stats.dueWeek} color="warning" />
      </div>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {[{v: "pos", l: "Purchase Orders"}, {v: "reqs", l: "Requirements"}, {v: "perf", l: "Supplier Performance"}].map(t => (
            <Tabs.Trigger key={t.v} value={t.v}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${tab === t.v ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t.l}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="pos">
          <Card padding="none">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["PO #", "Supplier", "Value", "Order Date", "Expected", "Status", "Days"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {pos.length === 0 ? (
                    <tr><td colSpan={7} className="text-center py-12 text-slate-400 text-sm">No purchase orders</td></tr>
                  ) : pos.map(p => {
                    const overdue = p.expected_delivery && new Date(p.expected_delivery) < new Date() && !["received", "closed"].includes(p.status)
                    return (
                      <tr key={p.id} className={`border-b border-slate-100 ${overdue ? "bg-red-50" : "hover:bg-slate-50"}`}>
                        <td className="px-3 py-2 font-mono text-xs">{p.po_number}</td>
                        <td className="px-3 py-2">{supplierMap[p.supplier_id] ?? p.supplier_id}</td>
                        <td className="px-3 py-2">${p.total_value?.toLocaleString()}</td>
                        <td className="px-3 py-2">{p.order_date}</td>
                        <td className="px-3 py-2">{p.expected_delivery}</td>
                        <td className="px-3 py-2"><Badge variant="muted">{p.status}</Badge></td>
                        <td className="px-3 py-2">{p.expected_delivery ? Math.round((new Date(p.expected_delivery).getTime() - Date.now()) / 86400000) : "—"}d</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="reqs">
          <Card title="MRP Requirements" subtitle="Net material requirements from production plan"
            headerAction={<Button size="sm" onClick={async () => {
              const r = await procurementApi.requirements(fid); setReqs((r.data as any[]) || [])
            }}><RefreshCw className="w-3 h-3" /> Refresh</Button>}>
            {reqs.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-sm">No requirements — all materials stocked</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      {["Material", "Period", "Gross", "On Hand", "Net", "Suggested PO", "Supplier"].map(h => (
                        <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {reqs.map((r, i) => (
                      <tr key={i} className="border-b border-slate-100">
                        <td className="px-3 py-2">{r.material_name}</td>
                        <td className="px-3 py-2">{r.period_date}</td>
                        <td className="px-3 py-2 text-right">{r.gross_requirement?.toFixed(0)}</td>
                        <td className="px-3 py-2 text-right">{r.on_hand?.toFixed(0)}</td>
                        <td className="px-3 py-2 text-right font-semibold text-red-600">{r.net_requirement?.toFixed(0)}</td>
                        <td className="px-3 py-2">{r.suggested_po_date}</td>
                        <td className="px-3 py-2">{r.preferred_supplier_name ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </Tabs.Content>

        <Tabs.Content value="perf">
          <div className="space-y-3">
            {perf.map(p => (
              <Card key={p.supplier_id} title={p.supplier_name} subtitle={`Rating: ${p.rating}/5 · Active POs: ${p.active_pos}`}>
                <div className="grid grid-cols-3 gap-4 mb-3">
                  <div>
                    <div className="text-xs text-slate-500">On-Time Delivery</div>
                    <div className="text-2xl font-bold text-green-600">{p.on_time_delivery_pct.toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Quality Acceptance</div>
                    <div className="text-2xl font-bold text-blue-600">{p.quality_acceptance_pct.toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Rating</div>
                    <div className="text-2xl font-bold text-yellow-600">{p.rating}/5</div>
                  </div>
                </div>
                <LineChart
                  data={(p.monthly_otd || []).map((m: any) => ({ month: m.month, OTD: m.value }))}
                  xKey="month"
                  lines={[{ key: "OTD", name: "OTD %", color: "#16A34A" }]}
                  height={120}
                />
              </Card>
            ))}
            {perf.length === 0 && <Card><div className="text-center py-8 text-slate-400 text-sm">No supplier performance data</div></Card>}
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
