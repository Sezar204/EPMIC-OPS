Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { DollarSign, TrendingUp, AlertTriangle } from "lucide-react"
import { costApi, productsApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { BarChart, LineChart } from "@/components/charts"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function Cost() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("costs")
  const [costs, setCosts]   = useState<any[]>([])
  const [variance, setVar] = useState<any>(null)
  const [profit, setProfit] = useState<any>(null)
  const [products, setProducts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      costApi.listProductCosts(fid),
      costApi.varianceAnalysis(fid),
      costApi.profitability(fid),
      productsApi.list(fid),
    ]).then(([c, v, p, pr]) => {
      setCosts((c.data as any[]) || [])
      setVar(v.data)
      setProfit(p.data)
      setProducts((pr.data as any[]) || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [fid])

  if (loading) return <PageSkeleton />

  const productMap: Record<number, any> = {}
  products.forEach(p => { productMap[p.id] = p })

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Cost & Profitability</h1>
      <p className="text-sm text-slate-500 mb-6">Standard vs actual cost analysis</p>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {[{v: "costs", l: "Product Costs"}, {v: "variance", l: "Variance Analysis"}, {v: "profit", l: "Profitability"}].map(t => (
            <Tabs.Trigger key={t.v} value={t.v}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${tab === t.v ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t.l}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="costs">
          <Card padding="none">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["Product", "Std Mat", "Act Mat", "Std Lab", "Act Lab", "Std OH", "Act OH", "Std Total", "Act Total", "Var %", "Status"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {costs.length === 0 ? (
                    <tr><td colSpan={11} className="text-center py-12 text-slate-400 text-sm">No cost data</td></tr>
                  ) : costs.map(c => (
                    <tr key={c.id} className="border-b border-slate-100">
                      <td className="px-3 py-2 font-medium">{productMap[c.product_id]?.sku ?? c.product_id}</td>
                      <td className="px-3 py-2 text-right">${c.std_material_cost?.toFixed(2)}</td>
                      <td className="px-3 py-2 text-right">${c.act_material_cost?.toFixed(2)}</td>
                      <td className="px-3 py-2 text-right">${c.std_labor_cost?.toFixed(2)}</td>
                      <td className="px-3 py-2 text-right">${c.act_labor_cost?.toFixed(2)}</td>
                      <td className="px-3 py-2 text-right">${c.std_overhead_cost?.toFixed(2)}</td>
                      <td className="px-3 py-2 text-right">${c.act_overhead_cost?.toFixed(2)}</td>
                      <td className="px-3 py-2 text-right font-semibold">${c.std_total_cost?.toFixed(2)}</td>
                      <td className="px-3 py-2 text-right font-semibold">${c.act_total_cost?.toFixed(2)}</td>
                      <td className={`px-3 py-2 text-right font-semibold ${Math.abs(c.variance_pct) < 5 ? "text-green-600" : Math.abs(c.variance_pct) < 10 ? "text-yellow-600" : "text-red-600"}`}>
                        {c.variance_pct?.toFixed(1)}%
                      </td>
                      <td className="px-3 py-2">
                        <Badge variant={c.status === "good" ? "success" : c.status === "warning" ? "warning" : "danger"}>
                          {c.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="variance">
          {variance && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <StatCard label="Total Variance" value={`$${variance.total_variance?.toFixed(0)}`} color="warning" />
                <StatCard label="Material"        value={`$${variance.material_variance?.toFixed(0)}`} color="info" />
                <StatCard label="Labor"           value={`$${variance.labor_variance?.toFixed(0)}`} color="primary" />
                <StatCard label="Overhead"        value={`$${variance.overhead_variance?.toFixed(0)}`} color="danger" />
              </div>
              <Card title="Variance by Product">
                <BarChart
                  data={(variance.by_product || []).map((p: any) => ({ name: p.product_sku, Variance: p.variance_pct }))}
                  xKey="name"
                  bars={[{ key: "Variance", name: "Variance %", color: "#D97706" }]}
                  height={280}
                />
              </Card>
            </>
          )}
        </Tabs.Content>

        <Tabs.Content value="profit">
          {profit && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <StatCard label="Revenue"  value={`$${profit.total_revenue?.toLocaleString()}`} color="success" icon={<DollarSign className="w-5 h-5" />} />
                <StatCard label="Cost"     value={`$${profit.total_cost?.toLocaleString()}`}    color="info" />
                <StatCard label="Profit"   value={`$${profit.gross_profit?.toLocaleString()}`} color="primary" icon={<TrendingUp className="w-5 h-5" />} />
                <StatCard label="Avg Margin" value={`${profit.avg_margin_pct?.toFixed(1)}%`}    color="warning" />
              </div>
              <Card title="Profitability by Product" padding="none">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        {["Product", "Revenue", "Cost", "Margin", "Margin %", "Trend"].map(h => (
                          <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(profit.rows || []).map((r: any) => (
                        <tr key={r.product_id} className={`border-b border-slate-100 ${r.margin_pct < 10 ? "bg-red-50" : ""}`}>
                          <td className="px-3 py-2 font-medium">{r.product_sku}</td>
                          <td className="px-3 py-2 text-right">${r.revenue?.toLocaleString()}</td>
                          <td className="px-3 py-2 text-right">${r.cost?.toLocaleString()}</td>
                          <td className="px-3 py-2 text-right">${r.margin?.toLocaleString()}</td>
                          <td className={`px-3 py-2 text-right font-semibold ${r.margin_pct < 10 ? "text-red-600" : r.margin_pct < 20 ? "text-yellow-600" : "text-green-600"}`}>
                            {r.margin_pct?.toFixed(1)}%
                          </td>
                          <td className="px-3 py-2 w-32">
                            <LineChart
                              data={(r.trend || []).map((v: number, i: number) => ({ i, v }))}
                              xKey="i" lines={[{ key: "v", name: "M%", color: r.margin_pct < 10 ? "#DC2626" : "#16A34A" }]}
                              height={32}
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          )}
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
