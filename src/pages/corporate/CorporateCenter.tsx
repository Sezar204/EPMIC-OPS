Input
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Building2, AlertTriangle, CheckCircle, TrendingUp, Zap, RefreshCw } from "lucide-react"
import { useAppStore } from "@/stores/appStore"
import { corporateApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { HealthGauge } from "@/components/ui/HealthGauge"
import { StatCard } from "@/components/ui/StatCard"
import { LineChart } from "@/components/charts"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function CorporateCenter() {
  const navigate = useNavigate()
  const { setCurrentFactory } = useAppStore()
  const [data, setData] = useState<any>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [decisions, setDecisions] = useState<any[]>([])
  const [kpis, setKpis] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    Promise.all([
      corporateApi.getOverview(),
      corporateApi.getCriticalAlerts(),
      corporateApi.getPendingDecisions(),
      corporateApi.getGroupKPIs(),
    ]).then(([o, a, d, k]) => {
      setData((o as any).data); setAlerts(((a as any).data) || []); setDecisions(((d as any).data) || []); setKpis((k as any).data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  if (loading) return <PageSkeleton />

  return (
    <div className="page-container">
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-slate-900 rounded-xl flex items-center justify-center">
            <Building2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">All Factories — Corporate View</h1>
            <p className="text-sm text-slate-500">Group-level performance and decision support</p>
          </div>
        </div>
        <Button variant="outline" onClick={load}><RefreshCw className="w-4 h-4" /> Refresh</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Output" value={kpis?.total_output?.toLocaleString() ?? "0"} unit="units" color="primary" />
        <StatCard label="Avg OEE" value={`${kpis?.avg_oee?.toFixed(1) ?? 0}%`} color="success" />
        <StatCard label="Avg OTIF" value={`${kpis?.avg_otif?.toFixed(1) ?? 0}%`} color="info" />
        <StatCard label="Avg Quality" value={`${kpis?.avg_quality?.toFixed(1) ?? 0}%`} color="warning" />
      </div>

      <h2 className="section-title">Factory Status</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 mb-6">
        {(data?.factories || []).map((f: any) => (
          <Card key={f.id} className="hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => { setCurrentFactory(f); navigate(`/factory/${f.id}/dashboard`) }}>
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs font-mono text-slate-500">{f.code}</div>
                <div className="text-base font-semibold text-slate-900 mt-0.5">{f.name}</div>
                <div className="mt-1.5 flex items-center gap-1.5">
                  <Badge variant="muted">{f.type.toUpperCase()}</Badge>
                  <Badge variant={f.status === "active" ? "success" : "warning"} dot>{f.status}</Badge>
                </div>
              </div>
              <HealthGauge score={f.health_score} status={f.health_status as any} size="sm" />
            </div>
            <div className="text-xs text-slate-500 mt-2 flex items-center gap-1">
              <Zap className="w-3 h-3" /> Click to enter workspace
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card title="Critical Alerts" subtitle={`${alerts.length} across all factories`}>
          {alerts.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm flex items-center justify-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500" /> All clear
            </div>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {alerts.slice(0, 10).map((a: any) => (
                <div key={a.id} className="flex items-start gap-2 p-2 rounded border border-slate-200 bg-slate-50">
                  <AlertTriangle className={`w-4 h-4 mt-0.5 ${a.severity === "emergency" ? "text-red-700" : "text-red-500"}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium">{a.title}</div>
                    <div className="text-[10px] text-slate-500">{a.factory_name} · {a.created_at?.slice(0, 16).replace("T", " ")}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="Pending Decisions" subtitle={`${decisions.length} across all factories`}>
          {decisions.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm">No pending decisions</div>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {decisions.slice(0, 10).map((d: any) => (
                <div key={d.id} className="border border-slate-200 rounded p-2.5 bg-white">
                  <div className="flex items-start gap-2">
                    <Badge variant={d.priority === "urgent" ? "danger" : d.priority === "high" ? "warning" : "info"}>
                      {d.priority}
                    </Badge>
                    <div className="flex-1">
                      <div className="text-xs font-semibold">{d.title}</div>
                      <div className="text-[10px] text-slate-500">Factory #{d.factory_id}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <Card title="7-Day Forecast" subtitle="Group-level output projection">
        <LineChart
          data={Array.from({ length: 7 }, (_, i) => ({
            day: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i],
            Output: 800 + Math.round(Math.random() * 200),
            Plan:   900,
          }))}
          xKey="day"
          lines={[
            { key: "Output", name: "Actual", color: "#1E40AF" },
            { key: "Plan",   name: "Plan",   color: "#D97706", dashed: true },
          ]}
          height={220}
        />
      </Card>
    </div>
  )
}
