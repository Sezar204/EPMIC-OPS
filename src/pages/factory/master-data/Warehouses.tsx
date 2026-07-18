Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus, Pencil, Trash2 } from "lucide-react"
import { ColumnDef } from "@tanstack/react-table"
import { warehousesApi } from "@/api/factories"
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
  code: z.string().min(1),
  name: z.string().min(1),
  type: z.enum(["raw_material", "wip", "finished_goods", "general"]).default("general"),
  total_capacity: z.coerce.number().min(0).default(0),
  capacity_unit: z.string().min(1).default("sqm"),
  storage_conditions: z.string().optional(),
  location: z.string().optional(),
  notes: z.string().optional(),
})
type Form = z.infer<typeof schema>

export default function WarehousesPage() {
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
    defaultValues: { type: "general", total_capacity: 0, capacity_unit: "sqm" },
  })

  const load = async () => {
    setLoading(true)
    try { const r = await warehousesApi.list(fid); setRows((r.data as any[]) || []) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const onSubmit = async (data: Form) => {
    try {
      if (editing) { await warehousesApi.update(fid, editing.id, data); notify("Warehouse updated", "success") }
      else         { await warehousesApi.create(fid, data); notify("Warehouse created", "success") }
      setOpen(false); setEditing(null); reset(); load()
    } catch { notify("Save failed", "error") }
  }
  const startEdit = (row: any) => {
    setEditing(row); setOpen(true)
    setTimeout(() => reset(row), 50)
  }
  const startNew = () => {
    setEditing(null); setOpen(true)
    setTimeout(() => reset({ type: "general", total_capacity: 0, capacity_unit: "sqm" }), 50)
  }

  const stats = {
    total: rows.length,
    capacity: rows.reduce((a, r) => a + Number(r.total_capacity || 0), 0),
  }

  const columns: ColumnDef<any>[] = [
    { accessorKey: "code", header: "Code" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "type", header: "Type", cell: ({ getValue }) => <Badge variant="muted">{String(getValue())}</Badge> },
    { accessorKey: "total_capacity", header: "Capacity", cell: ({ getValue }) => Number(getValue() || 0).toLocaleString() },
    { accessorKey: "capacity_unit", header: "Unit" },
    { accessorKey: "location", header: "Location" },
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
          <h1 className="text-2xl font-bold text-slate-900">Warehouses</h1>
          <p className="text-sm text-slate-500">Storage locations and capacity</p>
        </div>
        <Button onClick={startNew}><Plus className="w-4 h-4" /> Add Warehouse</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
        <StatCard label="Total" value={stats.total} color="primary" />
        <StatCard label="Total Capacity" value={stats.capacity.toLocaleString()} color="info" />
      </div>

      <Card padding="none"><div className="p-4">
        <Table data={rows} columns={columns} searchPlaceholder="Search warehouses..." />
      </div></Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? "Edit Warehouse" : "Add Warehouse"}
        size="md"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
          <Button form="w-form" type="submit">Save</Button>
        </>}
      >
        <form id="w-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Code" required {...register("code")} error={errors.code?.message} />
            <Input label="Name" required {...register("name")} error={errors.name?.message} />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <Select label="Type" required options={[
              { value: "raw_material", label: "Raw Material" },
              { value: "wip", label: "WIP" },
              { value: "finished_goods", label: "Finished Goods" },
              { value: "general", label: "General" },
            ]} {...register("type")} />
            <Input label="Capacity" type="number" step="0.1" {...register("total_capacity")} />
            <Input label="Unit" required {...register("capacity_unit")} />
          </div>
          <Input label="Storage Conditions" {...register("storage_conditions")} />
          <Input label="Location" {...register("location")} />
          <Input label="Notes" {...register("notes")} />
        </form>
      </SlideOver>

      <ConfirmDialog
        open={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          await warehousesApi.remove(fid, deleting.id)
          notify("Warehouse deleted", "success"); load()
        }}
        title="Delete Warehouse" message={`Delete "${deleting?.name}"?`} confirmLabel="Delete" danger
      />
    </div>
  )
}
