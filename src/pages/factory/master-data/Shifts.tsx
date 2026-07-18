Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus, Pencil, Trash2 } from "lucide-react"
import { ColumnDef } from "@tanstack/react-table"
import { shiftsApi } from "@/api/factories"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { Table } from "@/components/ui/Table"
import { SlideOver } from "@/components/ui/SlideOver"
import { ConfirmDialog } from "@/components/ui/ConfirmDialog"
import { useAppStore } from "@/stores/appStore"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

const schema = z.object({
  name: z.string().min(1),
  start_time: z.string().min(1),
  end_time: z.string().min(1),
  break_minutes: z.coerce.number().min(0).default(0),
  days_of_week: z.string().min(1).default("1,2,3,4,5"),
  headcount: z.coerce.number().min(1).default(1),
  is_active: z.boolean().default(true),
})
type Form = z.infer<typeof schema>

const DAYS = [
  { v: 1, l: "Mon" }, { v: 2, l: "Tue" }, { v: 3, l: "Wed" },
  { v: 4, l: "Thu" }, { v: 5, l: "Fri" }, { v: 6, l: "Sat" }, { v: 7, l: "Sun" },
]

export default function ShiftsPage() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<any | null>(null)
  const [deleting, setDeleting] = useState<any | null>(null)
  const [days, setDays] = useState<number[]>([1, 2, 3, 4, 5])

  const { register, handleSubmit, reset, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { break_minutes: 30, headcount: 1, is_active: true, days_of_week: "1,2,3,4,5" },
  })

  const load = async () => {
    setLoading(true)
    try { const r = await shiftsApi.list(fid); setRows((r.data as any[]) || []) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const onSubmit = async (data: Form) => {
    const payload = { ...data, days_of_week: days.join(",") }
    try {
      if (editing) { await shiftsApi.update(fid, editing.id, payload); notify("Shift updated", "success") }
      else         { await shiftsApi.create(fid, payload); notify("Shift created", "success") }
      setOpen(false); setEditing(null); reset(); load()
    } catch { notify("Save failed", "error") }
  }
  const startEdit = (row: any) => {
    setEditing(row); setOpen(true)
    setDays(String(row.days_of_week).split(",").map(Number))
    setTimeout(() => reset(row), 50)
  }
  const startNew = () => {
    setEditing(null); setOpen(true); setDays([1, 2, 3, 4, 5])
    setTimeout(() => reset({ break_minutes: 30, headcount: 1, is_active: true, days_of_week: "1,2,3,4,5" }), 50)
  }
  const toggleDay = (d: number) =>
    setDays((cur) => cur.includes(d) ? cur.filter(x => x !== d) : [...cur, d].sort())

  const stats = {
    total: rows.length,
    active: rows.filter(r => r.is_active).length,
    headcount: rows.reduce((a, r) => a + (r.headcount || 0), 0),
  }

  const columns: ColumnDef<any>[] = [
    { accessorKey: "name", header: "Name" },
    { accessorKey: "start_time", header: "Start" },
    { accessorKey: "end_time", header: "End" },
    { accessorKey: "break_minutes", header: "Break (min)" },
    { id: "days", header: "Days", cell: ({ row }) => {
        const ds = String(row.original.days_of_week || "").split(",").map((d: string) => Number(d))
        return <div className="flex gap-1">{DAYS.map(d => ds.includes(d.v) ?
          <span key={d.v} className="text-[10px] px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">{d.l}</span> :
          <span key={d.v} className="text-[10px] px-1.5 py-0.5 text-slate-300">{d.l}</span>)}</div>
      } },
    { accessorKey: "headcount", header: "Headcount" },
    { id: "active", header: "Active", cell: ({ getValue }) =>
        <Badge variant={getValue() ? "success" : "muted"}>{getValue() ? "Yes" : "No"}</Badge> },
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
          <h1 className="text-2xl font-bold text-slate-900">Shifts</h1>
          <p className="text-sm text-slate-500">Working hours and rotation</p>
        </div>
        <Button onClick={startNew}><Plus className="w-4 h-4" /> Add Shift</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <StatCard label="Total" value={stats.total} color="primary" />
        <StatCard label="Active" value={stats.active} color="success" />
        <StatCard label="Total Headcount" value={stats.headcount} color="info" />
      </div>

      <Card padding="none"><div className="p-4">
        <Table data={rows} columns={columns} searchPlaceholder="Search shifts..." />
      </div></Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? "Edit Shift" : "Add Shift"}
        size="md"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
          <Button form="s-form" type="submit">Save</Button>
        </>}
      >
        <form id="s-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <Input label="Name" required {...register("name")} error={errors.name?.message} />
          <div className="grid grid-cols-3 gap-3">
            <Input label="Start" type="time" required {...register("start_time")} />
            <Input label="End"   type="time" required {...register("end_time")} />
            <Input label="Break (min)" type="number" {...register("break_minutes")} />
          </div>
          <Input label="Headcount" type="number" {...register("headcount")} />
          <div>
            <label className="text-xs font-medium text-slate-700 mb-1 block">Days of Week</label>
            <div className="flex gap-2">
              {DAYS.map(d => (
                <button key={d.v} type="button" onClick={() => toggleDay(d.v)}
                  className={`px-3 py-1.5 text-xs rounded border ${days.includes(d.v) ? "bg-primary text-white border-primary" : "bg-white text-slate-600 border-slate-300"}`}>
                  {d.l}
                </button>
              ))}
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" {...register("is_active")} defaultChecked />
            Active
          </label>
        </form>
      </SlideOver>

      <ConfirmDialog
        open={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          await shiftsApi.remove(fid, deleting.id)
          notify("Shift deleted", "success"); load()
        }}
        title="Delete Shift" message={`Delete "${deleting?.name}"?`} confirmLabel="Delete" danger
      />
    </div>
  )
}
