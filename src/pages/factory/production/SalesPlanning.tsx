Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Plus, RefreshCw, CheckCircle, AlertTriangle, XCircle, Activity } from "lucide-react"
import { salesApi, productsApi, customersApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { SlideOver } from "@/components/ui/SlideOver"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { LineChart } from "@/components/charts"
import { useAppStore } from "@/stores/appStore"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function SalesPlanning() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [tab, setTab] = useState("b2b")
  const [orders, setOrders] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [ctpFor, setCtpFor] = useState<any | null>(null)
  const [ctpResult, setCtpResult] = useState<any | null>(null)
  const [products, setProducts] = useState<any[]>([])
  const [customers, setCustomers] = useState<any[]>([])

  useEffect(() => {
    Promise.all([
      salesApi.listOrders(fid),
      productsApi.list(fid),
      customersApi.list(fid),
    ]).then(([o, p, c]) => {
      setOrders((o.data as any[]) || [])
      setProducts((p.data as any[]) || [])
      setCustomers((c.data as any[]) || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [fid])

  const runCTP = async (order: any) => {
    setCtpFor(order); setCtpResult(null)
    try {
      const r = await salesApi.runCTP(fid, order.id)
      setCtpResult(r.data)
    } catch {
      notify("CTP analysis failed", "error")
      setCtpFor(null)
    }
  }

  const stats = {
    total: orders.length,
    confirmed: orders.filter(o => o.status === "confirmed").length,
    inProd: orders.filter(o => o.status === "in_production").length,
    atRisk: orders.filter(o => {
      if (!o.required_delivery) return false
      const days = (new Date(o.required_delivery).getTime() - Date.now()) / 86400000
      return days < 3 && days > -1 && o.status !== "delivered"
    }).length,
  }

  if (loading) return <PageSkeleton />

  const customerMap: Record<number, string> = {}
  customers.forEach(c => { customerMap[c.id] = c.name })

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Sales Planning</h1>
      <p className="text-sm text-slate-500 mb-6">Orders, demand forecasting, and S&OP</p>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {["b2b", "b2c", "sop"].map(t => (
            <Tabs.Trigger key={t} value={t}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${tab === t ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t === "b2b" ? "B2B Orders" : t === "b2c" ? "B2C Forecast" : "S&OP"}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="b2b">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <StatCard label="Total Orders" value={stats.total} color="primary" />
            <StatCard label="Confirmed" value={stats.confirmed} color="info" />
            <StatCard label="In Production" value={stats.inProd} color="warning" />
            <StatCard label="At Risk" value={stats.atRisk} color="danger" />
          </div>
          <Card padding="none">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["Order #", "Customer", "Value", "Required", "Status", "Days Left", "Actions"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {orders.length === 0 ? (
                    <tr><td colSpan={7} className="text-center py-12 text-slate-400 text-sm">No sales orders</td></tr>
                  ) : orders.map(o => {
                    const days = o.required_delivery ? Math.round((new Date(o.required_delivery).getTime() - Date.now()) / 86400000) : 0
                    const color = days < 0 ? "text-red-600" : days < 3 ? "text-yellow-600" : "text-slate-700"
                    return (
                      <tr key={o.id} className="border-b border-slate-100 hover:bg-slate-50">
                        <td className="px-3 py-2 font-mono text-xs">{o.order_number}</td>
                        <td className="px-3 py-2">{customerMap[o.customer_id] ?? o.customer_id}</td>
                        <td className="px-3 py-2">${o.total_value?.toLocaleString()}</td>
                        <td className="px-3 py-2">{o.required_delivery}</td>
                        <td className="px-3 py-2"><Badge variant="muted">{o.status}</Badge></td>
                        <td className={`px-3 py-2 font-semibold ${color}`}>{days}d</td>
                        <td className="px-3 py-2">
                          <Button size="sm" variant="outline" onClick={() => runCTP(o)}>Run CTP</Button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="b2c">
          <Card title="Demand Forecast" subtitle="3-month moving average" headerAction={
            <Button size="sm"><RefreshCw className="w-3 h-3" /> Generate</Button>
          }>
            <LineChart
              data={[
                { period: "W-3", Historical: 100, System: 110, Final: 110 },
                { period: "W-2", Historical: 120, System: 115, Final: 115 },
                { period: "W-1", Historical: 110, System: 118, Final: 118 },
                { period: "Now",  Historical: 0,   System: 120, Final: 125 },
                { period: "W+1", Historical: 0,   System: 125, Final: 125 },
              ]}
              xKey="period"
              lines={[
                { key: "Historical", name: "Historical", color: "#94A3B8", dashed: true },
                { key: "System",     name: "System Forecast", color: "#1E40AF" },
                { key: "Final",      name: "Final",      color: "#D97706" },
              ]}
              height={300}
            />
          </Card>
        </Tabs.Content>

        <Tabs.Content value="sop">
          <Card title="S&OP" subtitle="Sales & Operations Plan" headerAction={
            <Button><Activity className="w-4 h-4" /> Run S&OP Analysis</Button>
          }>
            <p className="text-sm text-slate-500 py-6 text-center">Click "Run S&OP Analysis" to compute consolidated B2B+B2C plan vs capacity.</p>
          </Card>
        </Tabs.Content>
      </Tabs.Root>

      <SlideOver
        open={!!ctpFor}
        onClose={() => { setCtpFor(null); setCtpResult(null) }}
        title={`CTP Analysis — ${ctpFor?.order_number}`}
        size="md"
      >
        {ctpResult ? (
          <div className="space-y-4">
            <div className={`p-3 rounded-lg border-2 ${
              ctpResult.risk === "red"   ? "bg-red-50 border-red-200" :
              ctpResult.risk === "yellow" ? "bg-yellow-50 border-yellow-200" :
                                            "bg-green-50 border-green-200"
            }`}>
              <div className="flex items-center gap-2">
                {ctpResult.risk === "red"   && <XCircle className="w-5 h-5 text-red-600" />}
                {ctpResult.risk === "yellow" && <AlertTriangle className="w-5 h-5 text-yellow-600" />}
                {ctpResult.risk === "green"  && <CheckCircle className="w-5 h-5 text-green-600" />}
                <div className="text-sm font-semibold">
                  {ctpResult.can_commit ? "Can commit" : "Cannot commit"} · Risk: {ctpResult.risk}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><div className="text-xs text-slate-500">Earliest Date</div><div className="font-semibold">{ctpResult.earliest_date}</div></div>
              <div><div className="text-xs text-slate-500">Committed Date</div><div className="font-semibold">{ctpResult.committed_date}</div></div>
              <div><div className="text-xs text-slate-500">Margin %</div><div className="font-semibold">{ctpResult.margin_pct}%</div></div>
              <div><div className="text-xs text-slate-500">Bottleneck</div><div className="font-semibold text-xs">{ctpResult.bottleneck || "—"}</div></div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-slate-400 text-sm">Analyzing...</div>
        )}
      </SlideOver>
    </div>
  )
}
