Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus, Pencil, Trash2, Upload } from "lucide-react"
import { ColumnDef } from "@tanstack/react-table"
import { productsApi } from "@/api/factories"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { Table } from "@/components/ui/Table"
import { SlideOver } from "@/components/ui/SlideOver"
import { ConfirmDialog } from "@/components/ui/ConfirmDialog"
import { useAppStore } from "@/stores/appStore"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

const schema = z.object({
  sku: z.string().min(1),
  name: z.string().min(1),
  category: z.string().optional(),
  unit_of_measure: z.string().min(1),
  standard_cost: z.coerce.number().min(0),
  selling_price: z.coerce.number().min(0),
  min_order_qty: z.coerce.number().min(0).default(1),
  lead_time_days: z.coerce.number().min(0).default(0),
  shelf_life_days: z.coerce.number().optional(),
  type: z.enum(["finished", "semi-finished"]).default("finished"),
  notes: z.string().optional(),
})
type Form = z.infer<typeof schema>

export default function ProductsPage() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<any | null>(null)
  const [deleting, setDeleting] = useState<any | null>(null)

  const { register, handleSubmit, reset, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { type: "finished", unit_of_measure: "pcs", min_order_qty: 1, lead_time_days: 0 },
  })

  const load = async () => {
    setLoading(true)
    try { const r = await productsApi.list(fid); setRows((r.data as any[]) || []) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const onSubmit = async (data: Form) => {
    try {
      if (editing) { await productsApi.update(fid, editing.id, data); notify("Product updated", "success") }
      else         { await productsApi.create(fid, data); notify("Product created", "success") }
      setOpen(false); setEditing(null); reset(); load()
    } catch { notify("Save failed", "error") }
  }
  const startEdit = (row: any) => {
    setEditing(row); setOpen(true)
    setTimeout(() => reset(row), 50)
  }
  const startNew = () => {
    setEditing(null); setOpen(true)
    setTimeout(() => reset({ type: "finished", unit_of_measure: "pcs", min_order_qty: 1, lead_time_days: 0 }), 50)
  }

  const stats = {
    total: rows.length,
    finished: rows.filter(r => r.type === "finished").length,
    semi: rows.filter(r => r.type === "semi-finished").length,
  }

  const columns: ColumnDef<any>[] = [
    { accessorKey: "sku", header: "SKU" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "category", header: "Category" },
    { accessorKey: "unit_of_measure", header: "Unit" },
    { accessorKey: "standard_cost", header: "Std Cost", cell: ({ getValue }) => `$${Number(getValue()).toFixed(2)}` },
    { accessorKey: "selling_price", header: "Price", cell: ({ getValue }) => `$${Number(getValue()).toFixed(2)}` },
    { id: "margin", header: "Margin %", cell: ({ row }) => {
        const c = Number(row.original.standard_cost)
        const p = Number(row.original.selling_price)
        if (!p) return "—"
        const m = ((p - c) / p) * 100
        const color = m >= 30 ? "text-green-600" : m >= 15 ? "text-yellow-600" : "text-red-600"
        return <span className={`font-semibold ${color}`}>{m.toFixed(0)}%</span>
      } },
    { accessorKey: "type", header: "Type", cell: ({ getValue }) => {
        const v = String(getValue() ?? "")
        return <Badge variant={v === "finished" ? "primary" : "muted"}>{v}</Badge>
      } },
    { id: "actions", header: "", cell: ({ row }) => (
        <div className="flex justify-end gap-1">
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
          <h1 className="text-2xl font-bold text-slate-900">Products</h1>
          <p className="text-sm text-slate-500">Finished and semi-finished goods</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Upload className="w-4 h-4" /> Import</Button>
          <Button onClick={startNew}><Plus className="w-4 h-4" /> Add Product</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <StatCard label="Total" value={stats.total} color="primary" />
        <StatCard label="Finished" value={stats.finished} color="success" />
        <StatCard label="Semi-Finished" value={stats.semi} color="info" />
      </div>

      <Card padding="none"><div className="p-4">
        <Table data={rows} columns={columns} searchPlaceholder="Search products..." />
      </div></Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? "Edit Product" : "Add Product"}
        size="lg"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
          <Button form="p-form" type="submit">Save</Button>
        </>}
      >
        <form id="p-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input label="SKU" required {...register("sku")} error={errors.sku?.message} />
            <Input label="Name" required {...register("name")} error={errors.name?.message} />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <Input label="Category" {...register("category")} />
            <Input label="Unit of Measure" required {...register("unit_of_measure")} />
            <Select label="Type" required options={[
              { value: "finished", label: "Finished" },
              { value: "semi-finished", label: "Semi-Finished" },
            ]} {...register("type")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Standard Cost" type="number" step="0.01" required {...register("standard_cost")} />
            <Input label="Selling Price" type="number" step="0.01" required {...register("selling_price")} />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <Input label="Min Order Qty" type="number" {...register("min_order_qty")} />
            <Input label="Lead Time (days)" type="number" {...register("lead_time_days")} />
            <Input label="Shelf Life (days)" type="number" {...register("shelf_life_days")} />
          </div>
          <Input label="Notes" {...register("notes")} />
        </form>
      </SlideOver>

      <ConfirmDialog
        open={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          await productsApi.remove(fid, deleting.id)
          notify("Product deleted", "success"); load()
        }}
        title="Delete Product" message={`Delete "${deleting?.name}"?`} confirmLabel="Delete" danger
      />
    </div>
  )
}
