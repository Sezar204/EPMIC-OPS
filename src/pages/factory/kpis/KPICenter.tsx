Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Plus, TrendingUp, TrendingDown } from "lucide-react"
import { kpisApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Sparkline } from "@/components/ui/Sparkline"
import { Modal } from "@/components/ui/Modal"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { useForm } from "react-hook-form"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

const CATS = ["all", "production", "sales", "inventory", "procurement", "quality", "maintenance", "financial", "custom"]

export default function KPICenter() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("all")
  const [kpis, setKpis] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const { register, handleSubmit, reset } = useForm()

  useEffect(() => {
    kpisApi.list(fid).then(r => {
      setKpis((r.data as any[]) || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [fid])

  if (loading) return <PageSkeleton />

  const filtered = tab === "all" ? kpis : kpis.filter(k => k.category === tab)

  const onSubmit = async (data: any) => {
    await kpisApi.createCustom(fid, data)
    setOpen(false); reset()
    kpisApi.list(fid).then(r => setKpis((r.data as any[]) || []))
  }

  return (
    <div className="page-container">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">KPI Center</h1>
          <p className="text-sm text-slate-500">Real-time performance metrics</p>
        </div>
        <Button onClick={() => setOpen(true)}><Plus className="w-4 h-4" /> Add Custom KPI</Button>
      </div>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4 overflow-x-auto">
          {CATS.map(c => (
            <Tabs.Trigger key={c} value={c}
              className={`px-3 py-1.5 text-xs font-medium border-b-2 capitalize whitespace-nowrap ${tab === c ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {c}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(k => {
            const change = k.change ?? 0
            const trend  = k.trend || []
            const tgt    = k.target_value
            const color  = !tgt ? "#1E40AF" :
              (k.higher_is_better ? (k.value >= tgt ? "#16A34A" : k.value >= tgt * 0.85 ? "#D97706" : "#DC2626")
                                  : (k.value <= tgt ? "#16A34A" : k.value <= tgt * 1.15 ? "#D97706" : "#DC2626"))
            return (
              <div key={k.id} className="card p-4 border-l-4" style={{ borderLeftColor: color }}>
                <div className="flex items-start justify-between mb-1">
                  <Badge variant="muted" size="sm">{k.category}</Badge>
                  <div className="flex items-center gap-0.5 text-[10px] font-semibold" style={{ color: change >= 0 ? "#16A34A" : "#DC2626" }}>
                    {change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {Math.abs(change).toFixed(1)}
                  </div>
                </div>
                <div className="text-sm font-semibold text-slate-900 mt-1">{k.name}</div>
                <div className="flex items-baseline gap-1 mt-1">
                  <span className="text-2xl font-bold" style={{ color }}>
                    {k.display_format === "currency" ? "$" : ""}{k.value?.toFixed(1)}{k.display_format === "percentage" ? "%" : ""}
                  </span>
                  {k.unit && k.display_format === "number" && <span className="text-xs text-slate-500">{k.unit}</span>}
                </div>
                {tgt !== null && tgt !== undefined && (
                  <div className="text-[10px] text-slate-500 mt-0.5">Target: {tgt}{k.display_format === "percentage" ? "%" : ""}</div>
                )}
                <div className="h-8 mt-2">
                  {trend.length > 0 ? <Sparkline data={trend} color={color} height={32} /> : <div className="text-[10px] text-slate-400 italic">no trend</div>}
                </div>
              </div>
            )
          })}
        </div>
        {filtered.length === 0 && <div className="text-center py-12 text-slate-400 text-sm">No KPIs in this category</div>}
      </Tabs.Root>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Add Custom KPI"
        footer={<>
          <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
          <Button form="kpi-form" type="submit">Save</Button>
        </>}
      >
        <form id="kpi-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <Input label="Name" required {...register("name")} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Code" required {...register("code")} />
            <Select label="Category" required options={[
              { value: "production", label: "Production" },
              { value: "sales", label: "Sales" },
              { value: "inventory", label: "Inventory" },
              { value: "procurement", label: "Procurement" },
              { value: "quality", label: "Quality" },
              { value: "maintenance", label: "Maintenance" },
              { value: "financial", label: "Financial" },
              { value: "custom", label: "Custom" },
            ]} {...register("category")} />
          </div>
          <Input label="Formula" {...register("formula")} placeholder="e.g. (output / capacity) * 100" />
          <div className="grid grid-cols-3 gap-3">
            <Input label="Unit" {...register("unit")} placeholder="%, $, d..." />
            <Input label="Target" type="number" step="0.01" {...register("target_value")} />
            <Select label="Format" required options={[
              { value: "number", label: "Number" },
              { value: "percentage", label: "Percentage" },
              { value: "currency", label: "Currency" },
            ]} {...register("display_format")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Warning Threshold" type="number" step="0.01" {...register("warning_threshold")} />
            <Input label="Critical Threshold" type="number" step="0.01" {...register("critical_threshold")} />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" {...register("higher_is_better")} defaultChecked /> Higher is better
          </label>
        </form>
      </Modal>
    </div>
  )
}
