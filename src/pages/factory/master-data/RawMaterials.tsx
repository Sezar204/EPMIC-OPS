Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus, Pencil, Trash2, Upload, Package } from "lucide-react"
import { ColumnDef } from "@tanstack/react-table"
import { rawMaterialsApi, inventoryApi } from "@/api/factories"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { Table } from "@/components/ui/Table"
import { Modal } from "@/components/ui/Modal"
import { SlideOver } from "@/components/ui/SlideOver"
import { ConfirmDialog } from "@/components/ui/ConfirmDialog"
import { useAppStore } from "@/stores/appStore"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

const schema = z.object({
  code: z.string().min(1),
  name: z.string().min(1),
  category: z.string().optional(),
  unit_of_measure: z.string().min(1),
  standard_cost: z.coerce.number().min(0),
  safety_stock_qty: z.coerce.number().min(0).default(0),
  reorder_point_qty: z.coerce.number().min(0).default(0),
  lead_time_days: z.coerce.number().min(0).default(0),
  shelf_life_days: z.coerce.number().optional(),
  storage_conditions: z.string().optional(),
  notes: z.string().optional(),
})
type Form = z.infer<typeof schema>

export default function RawMaterialsPage() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [rows, setRows] = useState<any[]>([])
  const [invMap, setInvMap] = useState<Record<number, any>>({})
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<any | null>(null)
  const [deleting, setDeleting] = useState<any | null>(null)
  const [stockFor, setStockFor] = useState<any | null>(null)

  const { register, handleSubmit, reset, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { unit_of_measure: "kg", safety_stock_qty: 0, reorder_point_qty: 0, lead_time_days: 0 },
  })

  const load = async () => {
    setLoading(true)
    try {
      const [m, inv] = await Promise.all([rawMaterialsApi.list(fid), inventoryApi.rawMaterials(fid)])
      setRows((m.data as any[]) || [])
      const map: Record<number, any> = {}
      ;(inv.data as any[] || []).forEach((i: any) => { map[i.material_id] = i })
      setInvMap(map)
    } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const onSubmit = async (data: Form) => {
    try {
      if (editing) { await rawMaterialsApi.update(fid, editing.id, data); notify("Material updated", "success") }
      else         { await rawMaterialsApi.create(fid, data); notify("Material created", "success") }
      setOpen(false); setEditing(null); reset(); load()
    } catch { notify("Save failed", "error") }
  }
  const startEdit = (row: any) => {
    setEditing(row); setOpen(true)
    setTimeout(() => reset(row), 50)
  }
  const startNew = () => {
    setEditing(null); setOpen(true)
    setTimeout(() => reset({ unit_of_measure: "kg", safety_stock_qty: 0, reorder_point_qty: 0, lead_time_days: 0 }), 50)
  }

  const stats = {
    total: rows.length,
    below: rows.filter(r => invMap[r.id] && invMap[r.id].qty_on_hand < r.safety_stock_qty).length,
    critical: rows.filter(r => invMap[r.id] && invMap[r.id].coverage_status === "critical").length,
  }

  const columns: ColumnDef<any>[] = [
    { accessorKey: "code", header: "Code" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "category", header: "Category" },
    { accessorKey: "unit_of_measure", header: "Unit" },
    { accessorKey: "safety_stock_qty", header: "Safety", cell: ({ getValue }) => Number(getValue()).toLocaleString() },
    { id: "on_hand", header: "On Hand", cell: ({ row }) => {
        const inv = invMap[row.original.id]
        return inv ? inv.qty_on_hand.toLocaleString() : "—"
      } },
    { id: "coverage", header: "Coverage", cell: ({ row }) => {
        const inv = invMap[row.original.id]
        if (!inv) return "—"
        return `${(inv.days_coverage ?? 0).toFixed(1)}d`
      } },
    { id: "status", header: "Status", cell: ({ row }) => {
        const inv = invMap[row.original.id]
        if (!inv) return <Badge variant="muted">—</Badge>
        const v = inv.coverage_status
        return <Badge variant={v === "critical" ? "danger" : v === "warning" ? "warning" : "success"}>
          {v.toUpperCase()}
        </Badge>
      } },
    { id: "actions", header: "", cell: ({ row }) => (
        <div className="flex justify-end gap-1">
          <Button size="sm" variant="ghost" onClick={() => setStockFor(row.original)} title="View stock">
            <Package className="w-3 h-3" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => startEdit(row.original)}><Pencil className="w-3 h-3" /></Button>
          <Button size="sm" variant="ghost" onClick={() => setDeleting(row.original)}><Trash2 className="w-3 h-3 text-red-500" /></Button>
        </div>
      ) },
  ]

  if (loading) return <PageSkeleton />

  return (
    <div className="page-container">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Raw Materials</h1>
          <p className="text-sm text-slate-500">Inventory items and stock levels</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Upload className="w-4 h-4" /> Import</Button>
          <Button onClick={startNew}><Plus className="w-4 h-4" /> Add Material</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <StatCard label="Total" value={stats.total} color="primary" />
        <StatCard label="Below Safety" value={stats.below} color="warning" />
        <StatCard label="Critical (<3d)" value={stats.critical} color="danger" />
      </div>

      <Card padding="none"><div className="p-4">
        <Table data={rows} columns={columns} searchPlaceholder="Search materials..." />
      </div></Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? "Edit Material" : "Add Material"}
        size="lg"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
          <Button form="rm-form" type="submit">Save</Button>
        </>}
      >
        <form id="rm-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Code" required {...register("code")} error={errors.code?.message} />
            <Input label="Name" required {...register("name")} error={errors.name?.message} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Category" {...register("category")} />
            <Input label="Unit of Measure" required {...register("unit_of_measure")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Standard Cost" type="number" step="0.01" required {...register("standard_cost")} />
            <Input label="Lead Time (days)" type="number" {...register("lead_time_days")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Safety Stock Qty" type="number" step="0.1" {...register("safety_stock_qty")} />
            <Input label="Reorder Point Qty" type="number" step="0.1" {...register("reorder_point_qty")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Shelf Life (days)" type="number" {...register("shelf_life_days")} />
            <Input label="Storage Conditions" {...register("storage_conditions")} placeholder="e.g. dry, cold" />
          </div>
          <Input label="Notes" {...register("notes")} />
        </form>
      </SlideOver>

      <ConfirmDialog
        open={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          await rawMaterialsApi.remove(fid, deleting.id)
          notify("Material deleted", "success"); load()
        }}
        title="Delete Material" message={`Delete "${deleting?.name}"?`} confirmLabel="Delete" danger
      />

      <Modal
        open={!!stockFor}
        onClose={() => setStockFor(null)}
        title={stockFor ? `Stock: ${stockFor.name}` : "Stock"}
        size="md"
      >
        {stockFor && invMap[stockFor.id] ? (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div><div className="text-xs text-slate-500">On Hand</div><div className="text-2xl font-bold">{invMap[stockFor.id].qty_on_hand.toLocaleString()}</div></div>
              <div><div className="text-xs text-slate-500">Available</div><div className="text-2xl font-bold">{invMap[stockFor.id].qty_available.toLocaleString()}</div></div>
              <div><div className="text-xs text-slate-500">Reserved</div><div className="text-lg font-semibold">{invMap[stockFor.id].qty_reserved.toLocaleString()}</div></div>
              <div><div className="text-xs text-slate-500">Safety</div><div className="text-lg font-semibold">{stockFor.safety_stock_qty.toLocaleString()}</div></div>
              <div><div className="text-xs text-slate-500">Coverage</div><div className="text-lg font-semibold">{invMap[stockFor.id].days_coverage.toFixed(1)} days</div></div>
              <div><div className="text-xs text-slate-500">Status</div>
                <Badge variant={invMap[stockFor.id].coverage_status === "critical" ? "danger" : invMap[stockFor.id].coverage_status === "warning" ? "warning" : "success"}>
                  {invMap[stockFor.id].coverage_status.toUpperCase()}
                </Badge>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-slate-500">No stock data</div>
        )}
      </Modal>
    </div>
  )
}
