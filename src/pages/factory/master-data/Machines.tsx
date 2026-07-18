Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus, Pencil, Trash2, Upload } from "lucide-react"
import { ColumnDef } from "@tanstack/react-table"
import { machinesApi, productionLinesApi } from "@/api/factories"
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
  code: z.string().min(1),
  name: z.string().min(1),
  line_id: z.coerce.number().optional(),
  type: z.string().optional(),
  capacity: z.coerce.number().optional(),
  capacity_unit: z.string().optional(),
  criticality: z.enum(["low", "medium", "high", "critical"]).default("medium"),
  status: z.enum(["active", "idle", "maintenance", "down"]).default("active"),
  notes: z.string().optional(),
})
type Form = z.infer<typeof schema>

export default function MachinesPage() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [rows, setRows] = useState<any[]>([])
  const [lines, setLines] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<any | null>(null)
  const [deleting, setDeleting] = useState<any | null>(null)

  const { register, handleSubmit, reset, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { criticality: "medium", status: "active" },
  })

  const load = async () => {
    setLoading(true)
    try {
      const [mr, lr] = await Promise.all([machinesApi.list(fid), productionLinesApi.list(fid)])
      setRows((mr.data as any[]) || [])
      setLines((lr.data as any[]) || [])
    } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const onSubmit = async (data: Form) => {
    try {
      if (editing) {
        await machinesApi.update(fid, editing.id, data)
        notify("Machine updated", "success")
      } else {
        await machinesApi.create(fid, data)
        notify("Machine created", "success")
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
    setTimeout(() => reset({ criticality: "medium", status: "active" }), 50)
  }

  const stats = {
    total: rows.length,
    active: rows.filter(r => r.status === "active").length,
    maint: rows.filter(r => r.status === "maintenance").length,
    down: rows.filter(r => r.status === "down").length,
  }

  const lineMap: Record<number, string> = {}
  lines.forEach(l => { lineMap[l.id] = l.name })

  const columns: ColumnDef<any>[] = [
    { accessorKey: "code", header: "Code" },
    { accessorKey: "name", header: "Name" },
    { id: "line", header: "Line", cell: ({ row }) => lineMap[row.original.line_id] ?? "—" },
    { accessorKey: "criticality", header: "Criticality", cell: ({ getValue }) => {
        const v = String(getValue() ?? "")
        const color = v === "critical" ? "danger" : v === "high" ? "warning" : "muted"
        return <Badge variant={color as any}>{v}</Badge>
      } },
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
          <h1 className="text-2xl font-bold text-slate-900">Machines</h1>
          <p className="text-sm text-slate-500">Equipment, criticality, and status</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Upload className="w-4 h-4" /> Import</Button>
          <Button onClick={startNew}><Plus className="w-4 h-4" /> Add Machine</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Total"   value={stats.total}  color="primary" />
        <StatCard label="Active"  value={stats.active} color="success" />
        <StatCard label="In Maintenance" value={stats.maint} color="warning" />
        <StatCard label="Down"    value={stats.down}   color="danger" />
      </div>

      <Card padding="none"><div className="p-4">
        <Table data={rows} columns={columns} searchPlaceholder="Search machines..." />
      </div></Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? "Edit Machine" : "Add Machine"}
        size="md"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
          <Button form="m-form" type="submit">Save</Button>
        </>}
      >
        <form id="m-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Code" required {...register("code")} error={errors.code?.message} />
            <Input label="Name" required {...register("name")} error={errors.name?.message} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Select label="Line" options={[{ value: "", label: "— None —" }, ...lines.map(l => ({ value: String(l.id), label: l.name }))]} {...register("line_id")} />
            <Input label="Type" {...register("type")} placeholder="e.g. filler, mixer" />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <Input label="Capacity" type="number" step="0.1" {...register("capacity")} />
            <Input label="Unit" {...register("capacity_unit")} placeholder="e.g. pcs/h" />
            <Select label="Criticality" required options={[
              { value: "low", label: "Low" },
              { value: "medium", label: "Medium" },
              { value: "high", label: "High" },
              { value: "critical", label: "Critical" },
            ]} {...register("criticality")} />
          </div>
          <Select label="Status" required options={[
            { value: "active", label: "Active" },
            { value: "idle", label: "Idle" },
            { value: "maintenance", label: "Maintenance" },
            { value: "down", label: "Down" },
          ]} {...register("status")} />
          <Input label="Notes" {...register("notes")} />
        </form>
      </SlideOver>

      <ConfirmDialog
        open={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          await machinesApi.remove(fid, deleting.id)
          notify("Machine deleted", "success"); load()
        }}
        title="Delete Machine"
        message={`Delete "${deleting?.name}"?`}
        confirmLabel="Delete"
        danger
      />
    </div>
  )
}
