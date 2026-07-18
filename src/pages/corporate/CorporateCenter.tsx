import { useCallback, useEffect, useState } from "react"
import { RefreshCw } from "lucide-react"
import { api } from "@/api/client"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"
import { PageSkeleton } from "@/components/ui/PageSkeleton"
import { StatCard } from "@/components/ui/StatCard"
import { useAppStore } from "@/stores/appStore"
interface CorporateData { total_output?: number; avg_oee?: number; avg_otif?: number; avg_quality?: number; factory_count?: number }
export default function CorporateCenter() {
  const notify = useAppStore((s) => s.notify); const [data, setData] = useState<CorporateData | null>(null); const [loading, setLoading] = useState(true)
  const load = useCallback(async () => { setLoading(true); try { setData((await api.get<{ data?: CorporateData }>("/corporate/group-kpis")).data ?? null) } catch { notify("Unable to load corporate KPIs", "error") } finally { setLoading(false) } }, [notify])
  useEffect(() => { void load() }, [load])
  if (loading) return <PageSkeleton />
  return <div className="page-container"><div className="flex items-start justify-between mb-6"><div><h1 className="text-2xl font-bold">Corporate Center</h1><p className="text-slate-500 mt-1">Group-level operational performance across all factories.</p></div><Button variant="outline" leftIcon={<RefreshCw className="w-4 h-4" />} onClick={() => void load()}>Refresh</Button></div><div className="grid grid-cols-2 xl:grid-cols-5 gap-4">{Object.entries(data ?? {}).map(([key, value]) => <StatCard key={key} label={key.replace(/_/g, " ")} value={typeof value === "number" ? value.toLocaleString() : String(value)} />)}</div><Card className="mt-6" title="Decision focus"><p className="text-slate-600">Use the factory hub to review critical alerts, capacity, inventory and action-ready decisions for each site.</p></Card></div>
}

