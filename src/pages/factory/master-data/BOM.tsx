Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { Plus, Trash2, ChevronRight, ChevronDown, X, ListTree } from "lucide-react"
import { bomApi, productsApi, rawMaterialsApi } from "@/api/factories"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { SlideOver } from "@/components/ui/SlideOver"
import { useAppStore } from "@/stores/appStore"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

interface Line {
  material_id: number
  quantity_required: number
  unit: string
  loss_factor_pct: number
  is_alternative: boolean
  sequence_no: number
}

export default function BOMPage() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [rows, setRows] = useState<any[]>([])
  const [products, setProducts] = useState<any[]>([])
  const [mats, setMats] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [expanded, setExpanded] = useState<number | null>(null)
  const [form, setForm] = useState({ product_id: 0, version: "1.0", name: "", status: "active", yield_pct: 100 })
  const [lines, setLines] = useState<Line[]>([])

  const load = async () => {
    setLoading(true)
    try {
      const [b, p, m] = await Promise.all([bomApi.list(fid), productsApi.list(fid), rawMaterialsApi.list(fid)])
      setRows((b.data as any[]) || [])
      setProducts((p.data as any[]) || [])
      setMats((m.data as any[]) || [])
    } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const submit = async () => {
    if (!form.product_id) { notify("Select a product", "error"); return }
    try {
      await bomApi.create(fid, { ...form, lines })
      notify("BOM created", "success")
      setOpen(false); setLines([]); setForm({ product_id: 0, version: "1.0", name: "", status: "active", yield_pct: 100 }); load()
    } catch { notify("Save failed", "error") }
  }

  const productMap: Record<number, string> = {}
  products.forEach(p => { productMap[p.id] = p.name })
  const matMap: Record<number, { name: string; code: string; cost: number }> = {}
  mats.forEach(m => { matMap[m.id] = { name: m.name, code: m.code, cost: m.standard_cost } })

  const addLine = () => setLines([...lines, { material_id: 0, quantity_required: 1, unit: "kg", loss_factor_pct: 0, is_alternative: false, sequence_no: lines.length + 1 }])
  const removeLine = (i: number) => setLines(lines.filter((_, idx) => idx !== i))
  const updateLine = (i: number, patch: Partial<Line>) => setLines(lines.map((l, idx) => idx === i ? { ...l, ...patch } : l))

  const totalCost = lines.reduce((acc, l) => acc + (matMap[l.material_id]?.cost ?? 0) * l.quantity_required, 0)

  if (loading) return <PageSkeleton />

  return (
    <div className="page-container">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">BOM / Recipes</h1>
          <p className="text-sm text-slate-500">Bill of Materials for finished products</p>
        </div>
        <Button onClick={() => setOpen(true)}><Plus className="w-4 h-4" /> Add BOM</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <StatCard label="Total BOMs" value={rows.length} color="primary" />
        <StatCard label="Active" value={rows.filter(r => r.status === "active").length} color="success" />
        <StatCard label="Products Covered" value={new Set(rows.map(r => r.product_id)).size} color="info" />
      </div>

      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600 w-8"></th>
                <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">Product</th>
                <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">Name</th>
                <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">Version</th>
                <th className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">Status</th>
                <th className="px-3 py-2 text-right text-[11px] font-semibold uppercase text-slate-600">Yield %</th>
                <th className="px-3 py-2 text-right text-[11px] font-semibold uppercase text-slate-600">Lines</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-12 text-slate-400 text-sm">No BOMs yet</td></tr>
              ) : rows.map(b => {
                const isOpen = expanded === b.id
                return (
                  <>
                    <tr key={b.id} className="border-b border-slate-100 hover:bg-slate-50 cursor-pointer"
                      onClick={() => setExpanded(isOpen ? null : b.id)}>
                      <td className="px-3 py-2">
                        {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                      </td>
                      <td className="px-3 py-2 font-medium text-slate-900">{productMap[b.product_id] ?? b.product_id}</td>
                      <td className="px-3 py-2 text-slate-700">{b.name}</td>
                      <td className="px-3 py-2 font-mono text-xs text-slate-500">{b.version}</td>
                      <td className="px-3 py-2"><Badge variant={b.status === "active" ? "success" : "muted"}>{b.status}</Badge></td>
                      <td className="px-3 py-2 text-right">{b.yield_pct}%</td>
                      <td className="px-3 py-2 text-right">{(b.lines || []).length}</td>
                    </tr>
                    {isOpen && (b.lines || []).length > 0 && (
                      <tr className="bg-slate-50">
                        <td colSpan={7} className="px-8 py-3">
                          <div className="text-xs text-slate-500 mb-1 font-semibold">BOM Lines</div>
                          <table className="w-full text-xs">
                            <thead><tr className="text-[10px] uppercase text-slate-500">
                              <th className="text-left py-1">Seq</th>
                              <th className="text-left py-1">Material</th>
                              <th className="text-right py-1">Qty</th>
                              <th className="text-left py-1">Unit</th>
                              <th className="text-right py-1">Loss %</th>
                            </tr></thead>
                            <tbody>
                              {b.lines.map((l: any) => (
                                <tr key={l.id} className="border-t border-slate-200">
                                  <td className="py-1">{l.sequence_no}</td>
                                  <td className="py-1">{matMap[l.material_id]?.name ?? l.material_id}</td>
                                  <td className="py-1 text-right">{l.quantity_required}</td>
                                  <td className="py-1">{l.unit}</td>
                                  <td className="py-1 text-right">{l.loss_factor_pct}%</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </td>
                      </tr>
                    )}
                  </>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setLines([]) }}
        title="Add BOM"
        size="lg"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setLines([]) }}>Cancel</Button>
          <Button onClick={submit}>Save BOM</Button>
        </>}
      >
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Select label="Product" required options={[{ value: "", label: "— Select —" }, ...products.map(p => ({ value: String(p.id), label: `${p.sku} — ${p.name}` }))]}
              value={String(form.product_id)} onChange={e => setForm({ ...form, product_id: Number(e.target.value) })} />
            <Input label="Version" value={form.version} onChange={e => setForm({ ...form, version: e.target.value })} />
          </div>
          <Input label="Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. Standard recipe v1" />
          <div className="grid grid-cols-2 gap-3">
            <Select label="Status" options={[
              { value: "active", label: "Active" },
              { value: "inactive", label: "Inactive" },
              { value: "draft", label: "Draft" },
            ]} value={form.status} onChange={e => setForm({ ...form, status: e.target.value })} />
            <Input label="Yield %" type="number" value={form.yield_pct} onChange={e => setForm({ ...form, yield_pct: Number(e.target.value) })} />
          </div>

          <div className="border-t border-slate-200 pt-3">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm font-semibold flex items-center gap-1">
                <ListTree className="w-4 h-4" /> BOM Lines
              </div>
              <Button size="sm" variant="outline" onClick={addLine}><Plus className="w-3 h-3" /> Add Line</Button>
            </div>
            {lines.length === 0 ? (
              <div className="text-center py-6 text-slate-400 text-xs">No lines yet</div>
            ) : (
              <div className="space-y-2">
                {lines.map((l, i) => (
                  <div key={i} className="grid grid-cols-12 gap-2 items-end p-2 bg-slate-50 rounded">
                    <div className="col-span-1 text-xs text-slate-500 text-center">{i + 1}</div>
                    <div className="col-span-4">
                      <Select label="" options={[{ value: "", label: "Material" }, ...mats.map(m => ({ value: String(m.id), label: m.name }))]}
                        value={String(l.material_id)} onChange={e => updateLine(i, { material_id: Number(e.target.value) })} />
                    </div>
                    <div className="col-span-2">
                      <Input label="" type="number" step="0.001" value={l.quantity_required} onChange={e => updateLine(i, { quantity_required: Number(e.target.value) })} />
                    </div>
                    <div className="col-span-2">
                      <Input label="" value={l.unit} onChange={e => updateLine(i, { unit: e.target.value })} />
                    </div>
                    <div className="col-span-2">
                      <Input label="" type="number" value={l.loss_factor_pct} onChange={e => updateLine(i, { loss_factor_pct: Number(e.target.value) })} />
                    </div>
                    <div className="col-span-1">
                      <Button size="sm" variant="ghost" onClick={() => removeLine(i)}><X className="w-3 h-3 text-red-500" /></Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {lines.length > 0 && (
              <div className="text-right text-xs text-slate-600 mt-2">
                Estimated material cost: <span className="font-semibold">${totalCost.toFixed(2)}</span>
              </div>
            )}
          </div>
        </div>
      </SlideOver>
    </div>
  )
}
