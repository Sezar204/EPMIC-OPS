Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus, Pencil, Trash2, Star } from "lucide-react"
import { ColumnDef } from "@tanstack/react-table"
import { suppliersApi } from "@/api/factories"
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
  contact_name: z.string().optional(),
  contact_email: z.string().email().optional().or(z.literal("")),
  contact_phone: z.string().optional(),
  payment_terms_days: z.coerce.number().optional(),
  rating: z.coerce.number().min(1).max(5).default(3),
  status: z.enum(["active", "inactive", "blacklisted"]).default("active"),
  notes: z.string().optional(),
})
type Form = z.infer<typeof schema>

function Stars({ value }: { value: number }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <Star key={i} className={`w-3.5 h-3.5 ${i <= value ? "fill-yellow-400 text-yellow-400" : "text-slate-300"}`} />
      ))}
    </div>
  )
}

export default function SuppliersPage() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<any | null>(null)
  const [deleting, setDeleting] = useState<any | null>(null)

  const { register, handleSubmit, reset, watch, setValue, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { status: "active", rating: 3 },
  })
  const rating = watch("rating")

  const load = async () => {
    setLoading(true)
    try { const r = await suppliersApi.list(fid); setRows((r.data as any[]) || []) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const onSubmit = async (data: Form) => {
    try {
      if (editing) { await suppliersApi.update(fid, editing.id, data); notify("Supplier updated", "success") }
      else         { await suppliersApi.create(fid, data); notify("Supplier created", "success") }
      setOpen(false); setEditing(null); reset(); load()
    } catch { notify("Save failed", "error") }
  }
  const startEdit = (row: any) => {
    setEditing(row); setOpen(true)
    setTimeout(() => reset(row), 50)
  }
  const startNew = () => {
    setEditing(null); setOpen(true)
    setTimeout(() => reset({ status: "active", rating: 3 }), 50)
  }

  const stats = {
    total: rows.length,
    active: rows.filter(r => r.status === "active").length,
    avg: rows.length ? (rows.reduce((a, r) => a + r.rating, 0) / rows.length).toFixed(1) : "—",
    blacklisted: rows.filter(r => r.status === "blacklisted").length,
  }

  const columns: ColumnDef<any>[] = [
    { accessorKey: "code", header: "Code" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "contact_name", header: "Contact" },
    { accessorKey: "payment_terms_days", header: "Payment (days)" },
    { id: "rating", header: "Rating", cell: ({ getValue }) => <Stars value={Number(getValue() || 0)} /> },
    { accessorKey: "status", header: "Status", cell: ({ getValue }) => {
        const v = String(getValue() ?? "")
        const color = v === "active" ? "success" : v === "blacklisted" ? "danger" : "muted"
        return <Badge variant={color as any}>{v}</Badge>
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
          <h1 className="text-2xl font-bold text-slate-900">Suppliers</h1>
          <p className="text-sm text-slate-500">Vendor master data</p>
        </div>
        <Button onClick={startNew}><Plus className="w-4 h-4" /> Add Supplier</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Total" value={stats.total} color="primary" />
        <StatCard label="Active" value={stats.active} color="success" />
        <StatCard label="Avg Rating" value={String(stats.avg)} unit="/ 5" color="warning" />
        <StatCard label="Blacklisted" value={stats.blacklisted} color="danger" />
      </div>

      <Card padding="none"><div className="p-4">
        <Table data={rows} columns={columns} searchPlaceholder="Search suppliers..." />
      </div></Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? "Edit Supplier" : "Add Supplier"}
        size="md"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
          <Button form="sp-form" type="submit">Save</Button>
        </>}
      >
        <form id="sp-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Code" required {...register("code")} error={errors.code?.message} />
            <Input label="Name" required {...register("name")} error={errors.name?.message} />
          </div>
          <Input label="Contact Name" {...register("contact_name")} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Contact Email" type="email" {...register("contact_email")} />
            <Input label="Contact Phone" {...register("contact_phone")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Payment Terms (days)" type="number" {...register("payment_terms_days")} />
            <Select label="Status" required options={[
              { value: "active", label: "Active" },
              { value: "inactive", label: "Inactive" },
              { value: "blacklisted", label: "Blacklisted" },
            ]} {...register("status")} />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-700 mb-1 block">Rating</label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map(i => (
                <button key={i} type="button" onClick={() => setValue("rating", i)}
                  className="p-0.5">
                  <Star className={`w-6 h-6 ${i <= Number(rating) ? "fill-yellow-400 text-yellow-400" : "text-slate-300"}`} />
                </button>
              ))}
            </div>
            <input type="hidden" {...register("rating")} />
          </div>
          <Input label="Notes" {...register("notes")} />
        </form>
      </SlideOver>

      <ConfirmDialog
        open={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          await suppliersApi.remove(fid, deleting.id)
          notify("Supplier deleted", "success"); load()
        }}
        title="Delete Supplier" message={`Delete "${deleting?.name}"?`} confirmLabel="Delete" danger
      />
    </div>
  )
}
