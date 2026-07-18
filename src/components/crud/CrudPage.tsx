import { useCallback, useEffect, useMemo, useState } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import type { ColumnDef } from "@tanstack/react-table"
import { Plus, Pencil, Trash2, Upload } from "lucide-react"

import { api } from "@/api/client"
import { useAppStore } from "@/stores/appStore"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { SlideOver } from "@/components/ui/SlideOver"
import { Modal } from "@/components/ui/Modal"
import { Table } from "@/components/ui/Table"
import { ConfirmDialog } from "@/components/ui/ConfirmDialog"
import { Card } from "@/components/ui/Card"
import { StatCard } from "@/components/ui/StatCard"
import { Badge } from "@/components/ui/Badge"
import { SearchBar } from "@/components/ui/SearchBar"
import { PAGE_SIZE } from "@/constants"

export type FieldType = "text" | "number" | "textarea" | "select" | "checkbox" | "date" | "time"

export interface FieldDef {
  name: string
  label: string
  type: FieldType
  required?: boolean
  options?: { value: string; label: string }[]
  placeholder?: string
  colSpan?: number
}

interface CrudPageProps {
  title: string
  entity: string
  summaryPath?: string
  columns: ColumnDef<any, any>[]
  fields: FieldDef[]
  searchable?: boolean
  rowActions?: (row: any, reload: () => void) => React.ReactNode
}

function buildSchema(fields: FieldDef[]) {
  const shape: Record<string, z.ZodTypeAny> = {}
  for (const f of fields) {
    if (f.type === "number") {
      let s = z.union([z.coerce.number(), z.literal("")]).optional()
      if (f.required) s = z.coerce.number({ invalid_type_error: "Required" })
      shape[f.name] = s
    } else if (f.type === "checkbox") {
      shape[f.name] = z.boolean().optional()
    } else {
      let s = z.string()
      if (f.required) s = z.string().min(1, "Required")
      else s = z.string().optional().or(z.literal(""))
      shape[f.name] = s
    }
  }
  return z.object(shape)
}

export function CrudPage({ title, entity, summaryPath, columns, fields, searchable, rowActions }: CrudPageProps) {
  const { factoryId } = useParams()
  const fid = Number(factoryId)
  const notify = useAppStore((s) => s.notify)
  const [rows, setRows] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [summary, setSummary] = useState<Record<string, any> | null>(null)
  const [editing, setEditing] = useState<any | null>(null)
  const [open, setOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<any | null>(null)
  const [importOpen, setImportOpen] = useState(false)

  const schema = useMemo(() => buildSchema(fields), [fields])

  const reload = useCallback(async () => {
    setLoading(true)
    try {
      const [listRes, sumRes] = await Promise.all([
        api.get(`/factories/${fid}/${entity}`, { page: 1, page_size: 200, search: search || undefined }),
        summaryPath ? api.get(`/factories/${fid}/${summaryPath}`) : Promise.resolve(null),
      ])
      setRows(listRes.data?.data ?? [])
      if (sumRes) setSummary(sumRes.data?.data ?? null)
    } catch (e) {
      notify("Failed to load data", "error")
    } finally {
      setLoading(false)
    }
  }, [fid, entity, summaryPath, search])

  useEffect(() => { reload() }, [reload])

  const defaultValues = useMemo(() => {
    const v: Record<string, any> = {}
    for (const f of fields) v[f.name] = f.type === "checkbox" ? false : ""
    if (editing) for (const f of fields) v[f.name] = editing[f.name] ?? (f.type === "checkbox" ? false : "")
    return v
  }, [editing, fields])

  const form = useForm({ resolver: zodResolver(schema), values: defaultValues })

  const onSubmit = async (data: any) => {
    const payload: Record<string, any> = {}
    for (const f of fields) {
      let val = data[f.name]
      if (f.type === "number") val = val === "" || val == null ? null : Number(val)
      else if (f.type === "checkbox") val = !!val
      payload[f.name] = val
    }
    try {
      if (editing) await api.put(`/factories/${fid}/${entity}/${editing.id}`, payload)
      else await api.post(`/factories/${fid}/${entity}`, payload)
      notify(editing ? "Updated successfully" : "Created successfully", "success")
      setOpen(false); setEditing(null); reload()
    } catch (e: any) {
      notify(e?.response?.data?.message ?? "Save failed", "error")
    }
  }

  const confirmDelete = async () => {
    if (!deleteTarget) return
    try {
      await api.delete(`/factories/${fid}/${entity}/${deleteTarget.id}`)
      notify("Deleted", "success"); reload()
    } catch { notify("Delete failed", "error") }
    setDeleteTarget(null)
  }

  const actionColumn: ColumnDef<any, any> = {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => (
      <div className="flex gap-1">
        <Button size="sm" variant="ghost" onClick={() => { setEditing(row.original); setOpen(true) }}><Pencil className="w-3.5 h-3.5" /></Button>
        <Button size="sm" variant="ghost" className="text-danger" onClick={() => setDeleteTarget(row.original)}><Trash2 className="w-3.5 h-3.5" /></Button>
        {rowActions?.(row.original, reload)}
      </div>
    ),
  }

  return (
    <div className="page-container">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-xl font-bold text-slate-900">{title}</h1>
        <div className="flex gap-2">
          <Button variant="outline" leftIcon={<Upload className="w-4 h-4" />} onClick={() => setImportOpen(true)}>Import Excel</Button>
          <Button leftIcon={<Plus className="w-4 h-4" />} onClick={() => { setEditing(null); setOpen(true) }}>Add {title.replace(/s$/, "")}</Button>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
          {Object.entries(summary).map(([k, v]) => (
            <StatCard key={k} label={k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
              value={typeof v === "number" ? v : String(v)} />
          ))}
        </div>
      )}

      {searchable && (
        <div className="mb-4"><SearchBar value={search} onChange={setSearch} placeholder={`Search ${title}...`} /></div>
      )}

      <Table
        data={rows} columns={[...columns, actionColumn]} isLoading={loading}
        emptyMessage={`No ${title.toLowerCase()} found`}
        emptyActionLabel={`Add ${title.replace(/s$/, "")}`} emptyAction={() => { setEditing(null); setOpen(true) }}
      />

      <SlideOver open={open} onClose={() => { setOpen(false); setEditing(null) }}
        title={editing ? `Edit ${title.replace(/s$/, "")}` : `Add ${title.replace(/s$/, "")}`}
        size="md"
        footer={<>
          <Button variant="outline" onClick={() => { setOpen(false); setEditing(null) }}>Cancel</Button>
          <Button onClick={form.handleSubmit(onSubmit)} loading={form.formState.isSubmitting}>Save</Button>
        </>}
      >
        <form className="grid grid-cols-2 gap-3">
          {fields.map((f) => (
            <div key={f.name} className={f.type === "textarea" || (f.colSpan ?? 1) === 2 ? "col-span-2" : ""}>
              {f.type === "select" ? (
                <Select label={f.label} required={f.required}
                  options={f.options ?? []} placeholder={f.placeholder}
                  {...form.register(f.name)} />
              ) : f.type === "textarea" ? (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{f.label}{f.required && <span className="text-danger ml-0.5">*</span>}</label>
                  <textarea className="w-full h-20 rounded-lg border border-border p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30" {...form.register(f.name)} />
                </div>
              ) : f.type === "checkbox" ? (
                <label className="flex items-center gap-2 text-sm text-slate-700 mt-6">
                  <input type="checkbox" {...form.register(f.name)} /> {f.label}
                </label>
              ) : (
                <Input label={f.label} required={f.required} type={f.type === "number" ? "number" : f.type === "date" || f.type === "time" ? f.type : "text"}
                  placeholder={f.placeholder} {...form.register(f.name)} error={form.formState.errors[f.name]?.message as string} />
              )}
            </div>
          ))}
        </form>
      </SlideOver>

      <ConfirmDialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={confirmDelete}
        title={`Delete ${title.replace(/s$/, "")}`} message="This action cannot be undone." confirmLabel="Delete" danger />

      <ImportModal open={importOpen} onClose={() => setImportOpen(false)} fid={fid} entity={entity} onDone={reload} />
    </div>
  )
}

function ImportModal({ open, onClose, fid, entity, onDone }: { open: boolean; onClose: () => void; fid: number; entity: string; onDone: () => void }) {
  const notify = useAppStore((s) => s.notify)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<any[]>([])
  const [stats, setStats] = useState<any>(null)
  const [busy, setBusy] = useState(false)

  const handleFile = async (f: File) => {
    setFile(f)
    try {
      const res = await api.upload(`/import/excel/${fid}/${entity}`, f)
      setStats(res.data)
      setPreview(res.data?.preview ?? [])
    } catch (e: any) { notify(e?.response?.data?.message ?? "Import failed", "error") }
  }

  const commit = async () => {
    if (!stats?.preview?.length) return
    setBusy(true)
    try {
      await api.post(`/import/excel/${fid}/${entity}/commit`, { rows: stats.preview })
      notify("Import committed", "success"); onDone(); onClose()
    } catch (e: any) { notify(e?.response?.data?.message ?? "Commit failed", "error") }
    finally { setBusy(false) }
  }

  return (
    <Modal open={open} onClose={onClose} title="Import Excel" size="lg"
      footer={<>
        <Button variant="outline" onClick={onClose}>Cancel</Button>
        <Button onClick={commit} loading={busy} disabled={!preview.length}>Import {preview.length} rows</Button>
      </>}
    >
      <input type="file" accept=".xlsx,.xls" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} className="mb-3" />
      {stats && <p className="text-xs text-slate-500 mb-2">{stats.total} rows · {stats.valid} valid · {stats.errors?.length ?? 0} errors</p>}
      {preview.length > 0 && (
        <div className="max-h-64 overflow-auto">
          <Table data={preview} columns={Object.keys(preview[0]).filter(k => !k.includes("_id")).map((k) => ({ accessorKey: k, header: k }))} isLoading={false} />
        </div>
      )}
    </Modal>
  )
}
