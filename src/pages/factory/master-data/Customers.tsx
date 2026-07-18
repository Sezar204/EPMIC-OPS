Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Plus, Pencil, Trash2, Star } from "lucide-react"
import { ColumnDef } from "@tanstack/react-table"
import { customersApi } from "@/api/factories"
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
  type: z.enum(["b2b", "b2c", "distributor"]).default("b2b"),
  priority: z.coerce.number().min(1).max(5).default(3),
  credit_limit: z.coerce.number().optional(),
  payment_terms_days: z.coerce.number().optional(),
  contact_name: z.string().optional(),
  contact_email: z.string().email().optional().or(z.literal("")),
  contact_phone: z.string().optional(),
  notes: z.string().optional(),
})
type Form = z.infer<typeof schema>

export default function CustomersPage() {
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
    defaultValues: { type: "b2b", priority: 3 },
  })
  const priority = watch("priority")

  const load = async () => {
    setLoading(true)
    try { const r = await customersApi.list(fid); setRows((r.data as any[]) || []) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [fid])

  const onSubmit = async (data: Form) => {
    try {
      if (editing) { await customersApi.update(fid, editing.id, data); notify("Customer updated", "success") }
      else         { await customersApi.create(fid, data); notify("Customer created", "success") }
      setOpen(false); setEditing(null); reset(); load()
    } catch { notify("Save failed", "error") }
  }
  const startEdit = (row: any) => {
    setEditing(row); setOpen(true)
    setTimeout(() => reset(row), 50)
  }
  const startNew = () => {
    setEditing(null); setOpen(true)
    setTimeout(() => reset({ type: "b2b", priority: 3 }), 50)
  }

  const stats = {
    total: rows.length,
    b2b: rows.filter(r => r.type === "b2b").length,
    b2c: rows.filter(r => r.type === "b2c").length,
    distributors: rows.filter(r => r.type === "distributor").length,
  }

  const columns: ColumnDef<any>[] = [
    { accessorKey: "code", header: "Code" },
    { accessorKey: "name", header: "Name" },
    { accessorKey: "type", header: "Type", cell: ({ getValue }) => <Badge variant="muted">{String(getValue())}</Badge> },
    { id: "priority", header: "Priority", cell: ({ getValue }) => (
        <div className="flex gap-0.5">
          {[1, 2, 3, 4, 5].map(i => (
            <Star key={i} className={`w-3 h-3 ${i <= Number(getValue() || 0) ? "fill-yellow-400 text-yellow-400" : "text-slate-300"}`} />
          ))}
        </div>
      ) },
    { accessorKey: "credit_limit", header: "Credit Limit", cell: ({ getValue }) => getValue() ? `$${Number(getValue()).toLocaleString()}` : "—" },
    { accessorKey: "payment_terms_days", header: "Payment Terms" },
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
          <h1 className="text-2xl font-bold text-slate-900">Customers</h1>
          <p className="text-sm text-slate-500">Customer master data</p>
        </div>
        <Button onClick={startNew}><Plus className="w-4 h-4" /> Add Customer</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Total" value={stats.total} color="primary" />
        <StatCard label="B2B" value={stats.b2b} color="info" />
        <StatCard label="B2C" value={stats.b2c} color="success" />
        <StatCard label="Distributors" value={stats.distributors} color="warning" />
      </div>

      <Card padding="none"><div className="p-4">
        <Table data={rows} columns={columns} searchPlaceholder="Search customers..." />
      </div></Card>

      <SlideOver
        open={open}
        onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? "Edit Customer" : "Add Customer"}
        size="md"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
          <Button form="c-form" type="submit">Save</Button>
        </>}
      >
        <form id="c-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Code" required {...register("code")} error={errors.code?.message} />
            <Input label="Name" required {...register("name")} error={errors.name?.message} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Select label="Type" required options={[
              { value: "b2b", label: "B2B" },
              { value: "b2c", label: "B2C" },
              { value: "distributor", label: "Distributor" },
            ]} {...register("type")} />
            <Input label="Credit Limit" type="number" {...register("credit_limit")} />
          </div>
          <Input label="Payment Terms (days)" type="number" {...register("payment_terms_days")} />
          <Input label="Contact Name" {...register("contact_name")} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Contact Email" type="email" {...register("contact_email")} />
            <Input label="Contact Phone" {...register("contact_phone")} />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-700 mb-1 block">Priority</label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map(i => (
                <button key={i} type="button" onClick={() => setValue("priority", i)}>
                  <Star className={`w-6 h-6 ${i <= Number(priority) ? "fill-yellow-400 text-yellow-400" : "text-slate-300"}`} />
                </button>
              ))}
            </div>
            <input type="hidden" {...register("priority")} />
          </div>
          <Input label="Notes" {...register("notes")} />
        </form>
      </SlideOver>

      <ConfirmDialog
        open={!!deleting}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          await customersApi.remove(fid, deleting.id)
          notify("Customer deleted", "success"); load()
        }}
        title="Delete Customer" message={`Delete "${deleting?.name}"?`} confirmLabel="Delete" danger
      />
    </div>
  )
}
