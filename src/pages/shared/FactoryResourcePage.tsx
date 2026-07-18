import { useCallback, useEffect, useMemo, useState } from "react"
import { useParams } from "react-router-dom"
import type { ColumnDef } from "@tanstack/react-table"
import { RefreshCw } from "lucide-react"
import { api } from "@/api/client"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"
import { PageSkeleton } from "@/components/ui/PageSkeleton"
import { Table } from "@/components/ui/Table"
import { useAppStore } from "@/stores/appStore"
type Row = Record<string, unknown>
interface ApiResult { data?: Row[] | Record<string, unknown> }
function display(value: unknown): string { if (value === null || value === undefined || value === "") return "-"; if (typeof value === "object") return Array.isArray(value) ? value.length + " items" : "Details"; return String(value) }
export function FactoryResourcePage({ title, endpoint, description }: { title: string; endpoint: string; description: string }) {
  const { factoryId } = useParams(); const notify = useAppStore((s) => s.notify); const [rows, setRows] = useState<Row[]>([]); const [loading, setLoading] = useState(true)
  const reload = useCallback(async () => { if (!factoryId) return; setLoading(true); try { const result = await api.get<ApiResult>("/factories/" + factoryId + "/" + endpoint, { page: 1, page_size: 100 }); const payload = result.data; setRows(Array.isArray(payload) ? payload : payload ? [payload] : []) } catch { notify("Unable to load " + title.toLowerCase(), "error"); setRows([]) } finally { setLoading(false) } }, [endpoint, factoryId, notify, title])
  useEffect(() => { void reload() }, [reload])
  const columns = useMemo<ColumnDef<Row, unknown>[]>(() => Array.from(new Set(rows.flatMap((row) => Object.keys(row)))).filter((key) => !key.endsWith("_id") && key !== "id").slice(0, 8).map((key) => ({ accessorKey: key, header: key.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase()), cell: ({ getValue }) => display(getValue()) })), [rows])
  if (loading && !rows.length) return <PageSkeleton />
  return <div className="page-container"><div className="flex items-start justify-between gap-4 mb-5"><div><h1 className="text-xl font-bold">{title}</h1><p className="text-sm text-slate-500 mt-1">{description}</p></div><Button variant="outline" leftIcon={<RefreshCw className="w-4 h-4" />} onClick={() => void reload()}>Refresh</Button></div><Card padding={false}><Table data={rows} columns={columns} isLoading={loading} emptyMessage={"No " + title.toLowerCase() + " found"} searchable /></Card></div>
}

