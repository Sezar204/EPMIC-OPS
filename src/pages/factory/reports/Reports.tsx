Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { FileText, FileSpreadsheet, FileCode, Download, Calendar } from "lucide-react"
import { reportsApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Badge } from "@/components/ui/Badge"
import { useAppStore } from "@/stores/appStore"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function Reports() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify } = useAppStore()
  const [reports, setReports] = useState<any[]>([])
  const [selected, setSelected] = useState<any | null>(null)
  const [params, setParams] = useState({ date_from: "", date_to: "" })
  const [preview, setPreview] = useState<any[] | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    reportsApi.library().then(r => {
      setReports((r.data as any[]) || [])
      if (r.data && (r.data as any[]).length > 0) setSelected((r.data as any[])[0])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <PageSkeleton />

  const cats = Array.from(new Set(reports.map(r => r.category)))
  const generate = async (fmt: string) => {
    if (!selected) return
    try {
      notify("Generating report…", "info")
      // We need a Blob response for file download — but our API returns Response
      // Simulate preview with the library data for now
      const blob = await reportsApi.generate(selected.id, params.date_from || null, params.date_to || null, fmt)
      const url  = URL.createObjectURL(blob as any)
      const a    = document.createElement("a")
      a.href = url
      a.download = `${selected.id}_${Date.now()}.${fmt === "excel" ? "xlsx" : fmt}`
      a.click()
      URL.revokeObjectURL(url)
      notify("Report downloaded", "success")
    } catch {
      notify("Report generation failed", "error")
    }
  }

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Reports</h1>
      <p className="text-sm text-slate-500 mb-6">Pre-built and custom reports</p>

      <div className="grid grid-cols-1 lg:grid-cols-[200px_1fr] gap-4">
        {/* Sidebar */}
        <Card padding="sm">
          <div className="space-y-3">
            {cats.map(cat => (
              <div key={cat}>
                <div className="text-[10px] font-bold uppercase text-slate-500 mb-1 tracking-wider">{cat}</div>
                <div className="space-y-1">
                  {reports.filter(r => r.category === cat).map(r => (
                    <button key={r.id} onClick={() => setSelected(r)}
                      className={`w-full text-left text-xs p-2 rounded transition-colors ${
                        selected?.id === r.id ? "bg-primary text-white" : "hover:bg-slate-100 text-slate-700"
                      }`}>
                      <div className="font-medium">{r.name}</div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Main */}
        <div className="space-y-4">
          {selected ? (
            <>
              <Card>
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">{selected.name}</h2>
                    <p className="text-sm text-slate-500 mt-1">{selected.description}</p>
                    <Badge variant="muted" className="mt-2">{selected.category}</Badge>
                  </div>
                  <FileText className="w-8 h-8 text-slate-300" />
                </div>
              </Card>

              <Card title="Parameters">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <Input label="Date From" type="date" value={params.date_from}
                    onChange={e => setParams({ ...params, date_from: e.target.value })} />
                  <Input label="Date To" type="date" value={params.date_to}
                    onChange={e => setParams({ ...params, date_to: e.target.value })} />
                  <div className="flex items-end">
                    <Button className="w-full"><Calendar className="w-4 h-4" /> Generate</Button>
                  </div>
                </div>
              </Card>

              <Card title="Export">
                <div className="flex gap-2">
                  <Button variant="outline" onClick={() => generate("excel")}>
                    <FileSpreadsheet className="w-4 h-4" /> Excel
                  </Button>
                  <Button variant="outline" onClick={() => generate("csv")}>
                    <FileCode className="w-4 h-4" /> CSV
                  </Button>
                  <Button variant="outline" onClick={() => generate("pdf")}>
                    <FileText className="w-4 h-4" /> PDF
                  </Button>
                </div>
              </Card>
            </>
          ) : (
            <Card><div className="text-center py-12 text-slate-400 text-sm">Select a report from the sidebar</div></Card>
          )}
        </div>
      </div>
    </div>
  )
}
