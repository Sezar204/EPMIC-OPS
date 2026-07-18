Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Package, AlertTriangle, TrendingUp, BarChart3 } from "lucide-react"
import { inventoryApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { Table } from "@/components/ui/Table"
import { PageSkeleton } from "@/components/ui/PageSkeleton"
import { ColumnDef } from "@tanstack/react-table"

export default function Inventory() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("raw")
  const [raw, setRaw]     = useState<any[]>([])
  const [wip, setWip]     = useState<any[]>([])
  const [fg, setFg]       = useState<any[]>([])
  const [abc, setAbc]     = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      inventoryApi.rawMaterials(fid),
      inventoryApi.wip(fid),
      inventoryApi.finishedGoods(fid),
      inventoryApi.abcxyz(fid),
    ]).then(([r, w, f, a]) => {
      setRaw((r.data as any[]) || [])
      setWip((w.data as any[]) || [])
      setFg((f.data as any[]) || [])
      setAbc(a.data as any)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [fid])

  if (loading) return <PageSkeleton />

  const rawCols: ColumnDef<any>[] = [
    { accessorKey: "material_code", header: "Code" },
    { accessorKey: "material_name", header: "Material" },
    { accessorKey: "qty_on_hand", header: "On Hand", cell: ({ getValue }) => Number(getValue()).toLocaleString() },
    { accessorKey: "qty_reserved", header: "Reserved" },
    { accessorKey: "qty_available", header: "Available" },
    { accessorKey: "safety_stock_qty", header: "Safety" },
    { id: "coverage", header: "Coverage", cell: ({ row }) => `${(row.original.days_coverage ?? 0).toFixed(1)}d` },
    { id: "status", header: "Status", cell: ({ row }) => {
        const v = row.original.coverage_status
        return <Badge variant={v === "critical" ? "danger" : v === "warning" ? "warning" : "success"}>{v?.toUpperCase()}</Badge>
      } },
  ]

  const fgCols: ColumnDef<any>[] = [
    { accessorKey: "product_sku", header: "SKU" },
    { accessorKey: "product_name", header: "Product" },
    { accessorKey: "qty_on_hand", header: "On Hand" },
    { accessorKey: "qty_reserved", header: "Reserved" },
    { accessorKey: "qty_available", header: "Available" },
    { accessorKey: "expiry_date", header: "Expiry" },
  ]

  const wipCols: ColumnDef<any>[] = [
    { accessorKey: "order_number", header: "Order #" },
    { accessorKey: "product_sku", header: "Product" },
    { accessorKey: "quantity", header: "Quantity" },
    { accessorKey: "stage", header: "Stage" },
    { accessorKey: "status", header: "Status" },
  ]

  const cellColors: Record<string, string> = {
    AX: "bg-red-100 text-red-800", AY: "bg-red-100 text-red-800", AZ: "bg-red-100 text-red-800",
    BX: "bg-yellow-100 text-yellow-800", BY: "bg-yellow-100 text-yellow-800", BZ: "bg-yellow-100 text-yellow-800",
    CX: "bg-green-100 text-green-800", CY: "bg-green-100 text-green-800", CZ: "bg-green-100 text-green-800",
  }

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Inventory</h1>
      <p className="text-sm text-slate-500 mb-6">Raw materials, WIP, finished goods, and analytics</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Total Items" value={raw.length + fg.length} color="primary" />
        <StatCard label="Critical" value={raw.filter(r => r.coverage_status === "critical").length} color="danger" />
        <StatCard label="Below Safety" value={raw.filter(r => r.qty_on_hand < r.safety_stock_qty).length} color="warning" />
        <StatCard label="Total Value" value={`$${(abc?.total_value || 0).toLocaleString()}`} color="info" />
      </div>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {[
            { v: "raw", l: "Raw Materials" },
            { v: "wip", l: "WIP" },
            { v: "fg",  l: "Finished Goods" },
            { v: "abc", l: "Analysis" },
          ].map(t => (
            <Tabs.Trigger key={t.v} value={t.v}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${tab === t.v ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t.l}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="raw">
          <Card padding="none"><div className="p-4">
            <Table data={raw} columns={rawCols} searchPlaceholder="Search materials..." />
          </div></Card>
        </Tabs.Content>

        <Tabs.Content value="wip">
          <Card padding="none"><div className="p-4">
            <Table data={wip} columns={wipCols} searchPlaceholder="Search WIP..." />
          </div></Card>
        </Tabs.Content>

        <Tabs.Content value="fg">
          <Card padding="none"><div className="p-4">
            <Table data={fg} columns={fgCols} searchPlaceholder="Search products..." />
          </div></Card>
        </Tabs.Content>

        <Tabs.Content value="abc">
          <Card title="ABC/XYZ Matrix" subtitle="Value (A/B/C) × Volatility (X/Y/Z)">
            {abc ? (
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-2 max-w-2xl">
                  {["AX", "AY", "AZ", "BX", "BY", "BZ", "CX", "CY", "CZ"].map(cell => {
                    const data = abc.matrix?.find((c: any) => c.cell === cell) || { count: 0, total_value: 0 }
                    return (
                      <div key={cell} className={`p-4 rounded-lg ${cellColors[cell] || "bg-slate-100"}`}>
                        <div className="text-xs font-semibold">{cell}</div>
                        <div className="text-xl font-bold mt-1">{data.count}</div>
                        <div className="text-[10px] mt-1">${Math.round(data.total_value).toLocaleString()}</div>
                      </div>
                    )
                  })}
                </div>
                <div className="text-xs text-slate-500">
                  A = high value items (top 20%) · B = mid value (50%) · C = low value (bottom 30%)<br/>
                  X = stable demand (variance &lt; 20%) · Y = variable · Z = erratic
                </div>
              </div>
            ) : <div className="text-slate-400 text-sm py-6 text-center">No data</div>}
          </Card>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
