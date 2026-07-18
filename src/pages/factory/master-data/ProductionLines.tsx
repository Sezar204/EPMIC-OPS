Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus, Pencil, Trash2, Upload, Download } from "lucide-react"
import { ColumnDef } from "@tanstack/react-table"
import { productionLinesApi } from "@/api/factories"
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
import { STATUS_COLORS } from "@/constants"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

const schema = z.object({
  code: z.string().min(1, "Code is required"),
  name: z.string().min(1, "Name is required"),
  type: z.enum(["discrete", "process", "batch"]),
  capacity_per_hour: z.coerce.number().min(0),
  capacity_unit: z.string().min(1),
  changeover_minutes: z.coerce.number().min(0).default(0),
  status: z.enum(["active", "idle", "maintenance", "down"]).default("active"),
  notes: z.string().optional(),
})
type Form = z.infer<typeof schema>

export default function ProductionLinesPage() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<any | null>(null)
  const [deleting, setDeleting] = useState<any | null>(null)

  const { register, handleSubmit, reset, formState: { errors }, setValue } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { type: "discrete", capacity_unit: "pcs", status: "active", changeover_minutes: 0 },
  })

  const load = async () => {
    setLoading(true)
    try {
      const r = await productionLinesApi.list(fid)
      setRows((r.data as any[]) || [])
    } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const onSubmit = async (data: Form) => {
    try {
      if (editing) {
        await productionLinesApi.update(fid, editing.id, data)
        notify("Line updated", "success")
      } else {
        await productionLinesApi.create(fid, data)
        notify("Line created", "success")
      }
      setOpen(false); setEditing(null); reset(); load()
    } catch { notify("Save failed", "error") }
  }

  const startEdit = (row: any) => {
    setEditing(row); setOpen(true)
    setTimeout(() => reset(row), 50)
  }

  const startNew = () => {
    setEditing(null); setOpen(true)
    setTimeout(() => reset({ type: "discrete", capacity_unit: "pcs", status: "active", changeover_minutes: 0 }), 50)
  }

  const stats = {
    total: rows.length,
    active: rows.filter(r => r.status === "active").length,
    idle:   rows.filter(r => r.status === "idle").length,
    down:   rows.filter(r => r.status === "down").length,
  }

  const columns: ColumnDef<any>[] = [
    { accessorKey: "code", header: "Code" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "type", header: "Type" },
    { accessorKey: "capacity_per_hour", header: "Cap/hr", cell: ({ getValue }) => Number(getValue()).toLocaleString() },
    { accessorKey: "capacity_unit", header: "Unit" },
    { accessorKey: "changeover_minutes", header: "Changeover (min)" },
    { accessorKey: "status", header: "Status", cell: ({ getValue }) => {
        const v = String(getValue() ?? "")
        return <Badge variant="muted" className={STATUS_COLORS[v] || ""}>{v}</Badge>
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
          <h1 className="text-2xl font-bold text-slate-900">Production Lines</h1>
          <p className="text-sm text-slate-500">Manage your manufacturing lines and capacity</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Upload className="w-4 h-4" /> Import</Button>
          <Button onClick={startNew}><Plus className="w-4 h-4" /> Add Line</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Total"   value={stats.total}  color="primary" />
        <StatCard label="Active"  value={stats.active} color="success" />
        <StatCard label="Idle"    value={stats.idle}   color="warning" />
        <StatCard label="Down"    value={stats.down}   color="danger" />
      </div>

      <Card padding="none">
        <div className="p-4">
          <Table data={rows} columns={columns} searchPlaceholder="Search lines..." />
        </div>
      </Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? "Edit Production Line" : "Add Production Line"}
        size="md"
        footer={
          <>
            <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
            <Button form="line-form" type="submit">Save</Button>
          </>
        }
      >
        <form id="line-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Code" required error={errors.code?.message} {...register("code")}
              onChange={(e) => setValue("code", e.target.value.toUpperCase())} />
            <Input label="Name" required error={errors.name?.message} {...register("name")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Select label="Type" required options={[
              { value: "discrete", label: "Discrete" },
              { value: "process", label: "Process" },
              { value: "batch", label: "Batch" },
            ]} {...register("type")} />
            <Select label="Status" required options={[
              { value: "active", label: "Active" },
              { value: "idle", label: "Idle" },
              { value: "maintenance", label: "Maintenance" },
              { value: "down", label: "Down" },
            ]} {...register("status")} />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <Input label="Capacity/hr" type="number" step="0.1" required {...register("capacity_per_hour")} />
            <Input label="Unit" required {...register("capacity_unit")} />
            <Input label="Changeover (min)" type="number" {...register("changeover_minutes")} />
          </div>
          <Input label="Notes" {...register("notes")} />
        </form>
      </SlideOver>

      <ConfirmDialog
        open={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          await productionLinesApi.remove(fid, deleting.id)
          notify("Line deleted", "success")
          load()
        }}
        title="Delete Production Line"
        message={`Delete "${deleting?.name}"? This can be undone by an admin.`}
        confirmLabel="Delete"
        danger
      />
    </div>
  )
}
