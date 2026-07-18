Input
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Factory, Plus, Network, AlertTriangle, Activity, TrendingUp, Building2 } from "lucide-react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { factoriesApi } from "@/api/factories"
import { corporateApi } from "@/api/system"
import { useAppStore } from "@/stores/appStore"
import { Card }      from "@/components/ui/Card"
import { Button }    from "@/components/ui/Button"
import { Input }     from "@/components/ui/Input"
import { Select }    from "@/components/ui/Select"
import { Badge }     from "@/components/ui/Badge"
import { StatCard }  from "@/components/ui/StatCard"
import { HealthGauge } from "@/components/ui/HealthGauge"
import { Modal }     from "@/components/ui/Modal"
import { EmptyState } from "@/components/ui/EmptyState"
import { PageSkeleton } from "@/components/ui/PageSkeleton"
import { FACTORY_TYPES, CURRENCIES, APP_NAME, APP_TAGLINE } from "@/constants"
import type { Factory, FactoryHealthScore } from "@/types"

const factorySchema = z.object({
  name: z.string().min(2, "Name is required"),
  code: z.string().min(2, "Code is required").max(32),
  type: z.enum(["b2b", "b2c", "hybrid"]),
  location: z.string().optional(),
  currency: z.string().min(1),
  working_start: z.string().min(1),
  working_end:   z.string().min(1),
  notes: z.string().optional(),
})
type FactoryForm = z.infer<typeof factorySchema>

export default function ManufacturingHub() {
  const navigate = useNavigate()
  const { factories, setFactories, setCurrentFactory, notify } = useAppStore()
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [healthMap, setHealthMap] = useState<Record<number, FactoryHealthScore>>({})
  const [summary, setSummary] = useState<{ total: number; active: number; critical: number; avg: number }>({
    total: 0, active: 0, critical: 0, avg: 0,
  })

  const { register, handleSubmit, formState: { errors }, reset, setValue, watch } =
    useForm<FactoryForm>({
      resolver: zodResolver(factorySchema),
      defaultValues: { type: "hybrid", currency: "USD", working_start: "08:00", working_end: "17:00" },
    })
  const nameVal = watch("name")

  useEffect(() => {
    if (nameVal) {
      const code = nameVal.toUpperCase().replace(/[^A-Z0-9]+/g, "-").slice(0, 16)
      setValue("code", code)
    }
  }, [nameVal, setValue])

  const load = async () => {
    setLoading(true)
    try {
      const r = await factoriesApi.getAll()
      const items = (r.data as Factory[]) || []
      setFactories(items)

      const corp = await corporateApi.getOverview().catch(() => null)
      if (corp?.data) {
        const d = corp.data as { summary: typeof summary }
        setSummary(d.summary)
      }

      const hm: Record<number, FactoryHealthScore> = {}
      await Promise.allSettled(
        items.map(async (f) => {
          try {
            const hr = await factoriesApi.getHealthScore(f.id)
            if (hr.data) hm[f.id] = hr.data
          } catch { /* skip */ }
        })
      )
      setHealthMap(hm)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const onSubmit = async (data: FactoryForm) => {
    setSubmitting(true)
    try {
      const r = await factoriesApi.create(data)
      notify("Factory created successfully", "success")
      setShowAdd(false)
      reset()
      await load()
      if (r.data) {
        const f = r.data as Factory
        setCurrentFactory(f)
        navigate(`/factory/${f.id}/dashboard`)
      }
    } catch (e) {
      notify("Failed to create factory", "error")
    } finally {
      setSubmitting(false)
    }
  }

  const enterFactory = (f: Factory) => {
    setCurrentFactory(f)
    navigate(`/factory/${f.id}/dashboard`)
  }

  if (loading) return <PageSkeleton />

  return (
    <div className="page-container">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Factory className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{APP_NAME}</h1>
            <p className="text-sm text-slate-500">{APP_TAGLINE}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate("/corporate")}>
            <Building2 className="w-4 h-4" /> Corporate View
          </Button>
          <Button onClick={() => setShowAdd(true)}>
            <Plus className="w-4 h-4" /> Add Factory
          </Button>
        </div>
      </div>

      {/* Group summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Factories" value={summary.total || factories.length}
          icon={<Factory className="w-5 h-5" />} color="primary" />
        <StatCard label="Active Factories" value={summary.active || factories.filter(f => f.status === "active").length}
          icon={<Activity className="w-5 h-5" />} color="success" />
        <StatCard label="Critical Alerts" value={summary.critical}
          icon={<AlertTriangle className="w-5 h-5" />} color="danger" />
        <StatCard label="Avg Health Score" value={summary.avg ? Math.round(summary.avg) : "—"}
          unit="/ 100" icon={<TrendingUp className="w-5 h-5" />} color="info" />
      </div>

      {/* Factory grid */}
      {factories.length === 0 ? (
        <Card>
          <EmptyState
            icon={<Factory className="w-10 h-10" />}
            title="No factories yet"
            description="Get started by creating your first manufacturing plant."
            actionLabel="Add First Factory"
            onAction={() => setShowAdd(true)}
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {factories.map((f) => {
            const h = healthMap[f.id]
            return (
              <Card key={f.id} className="hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="text-xs font-mono text-slate-500">{f.code}</div>
                    <div className="text-base font-semibold text-slate-900 mt-0.5">{f.name}</div>
                    <div className="mt-1.5 flex items-center gap-1.5">
                      <Badge variant="muted">{f.type.toUpperCase()}</Badge>
                      <Badge variant={f.status === "active" ? "success" : "warning"} dot>
                        {f.status}
                      </Badge>
                    </div>
                  </div>
                  {h && <HealthGauge score={h.total_score} size="sm" />}
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs mb-4">
                  <div>
                    <div className="text-slate-500">Alerts</div>
                    <div className="font-semibold text-slate-900 mt-0.5">—</div>
                  </div>
                  <div>
                    <div className="text-slate-500">Plan Adherence</div>
                    <div className="font-semibold text-slate-900 mt-0.5">
                      {h ? `${h.plan_adherence.toFixed(0)}%` : "—"}
                    </div>
                  </div>
                </div>

                <Button className="w-full" onClick={() => enterFactory(f)}>
                  <Network className="w-4 h-4" /> Enter Workspace
                </Button>
              </Card>
            )
          })}
        </div>
      )}

      <Modal
        open={showAdd}
        onClose={() => setShowAdd(false)}
        title="Add Factory"
        description="Create a new manufacturing plant"
        size="lg"
        footer={
          <>
            <Button variant="outline" onClick={() => setShowAdd(false)}>Cancel</Button>
            <Button form="add-factory-form" type="submit" loading={submitting}>Create</Button>
          </>
        }
      >
        <form id="add-factory-form" onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input label="Factory Name" required error={errors.name?.message}
              {...register("name")} placeholder="e.g. Cairo Plant" />
            <Input label="Factory Code" required error={errors.code?.message}
              {...register("code")} placeholder="e.g. CAI-01" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Select label="Type" required options={FACTORY_TYPES} {...register("type")} />
            <Input label="Location" {...register("location")} placeholder="e.g. Cairo, Egypt" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Select label="Currency" required options={CURRENCIES} {...register("currency")} />
            <div></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Working Start" type="time" required {...register("working_start")} />
            <Input label="Working End"   type="time" required {...register("working_end")} />
          </div>
          <Input label="Notes" {...register("notes")} placeholder="Optional notes…" />
        </form>
      </Modal>
    </div>
  )
}
