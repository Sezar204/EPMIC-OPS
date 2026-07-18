Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Plus, Users } from "lucide-react"
import { workforceApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/ui/StatCard"
import { LineChart, BarChart } from "@/components/charts"
import { useForm } from "react-hook-form"
import { PageSkeleton } from "@/components/ui/PageSkeleton"

export default function Workforce() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const [tab, setTab] = useState("workers")
  const [workers, setWorkers] = useState<any[]>([])
  const [att, setAtt]       = useState<any[]>([])
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [skillInput, setSkillInput] = useState("")
  const [skills, setSkills] = useState<string[]>([])

  const { register, handleSubmit, reset } = useForm({
    defaultValues: { employee_id: "", name: "", department: "", role: "", status: "active" },
  })

  const load = () => {
    setLoading(true)
    const today = new Date().toISOString().slice(0, 10)
    Promise.all([
      workforceApi.listWorkers(fid),
      workforceApi.listAttendance(fid, today),
      workforceApi.metrics(fid),
    ]).then(([w, a, m]) => {
      setWorkers((w.data as any[]) || [])
      setAtt((a.data as any[]) || [])
      setMetrics(m.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }
  useEffect(() => { load() }, [fid])

  if (loading) return <PageSkeleton />

  const onSubmit = async (data: any) => {
    await workforceApi.createWorker(fid, { ...data, skills })
    setOpen(false); reset(); setSkills([]); setSkillInput(""); load()
  }

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Workforce</h1>
      <p className="text-sm text-slate-500 mb-6">Workers, shifts, attendance, and metrics</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <StatCard label="Attendance" value={`${metrics?.attendance_rate_pct?.toFixed(1) ?? 0}%`} color="success" />
        <StatCard label="Absenteeism" value={`${metrics?.absenteeism_pct?.toFixed(1) ?? 0}%`} color="danger" />
        <StatCard label="OT Hours" value={metrics?.total_ot_hours?.toFixed(1) ?? 0} color="warning" />
        <StatCard label="Headcount" value={metrics?.headcount ?? 0} color="primary" />
      </div>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {["workers", "shifts", "attendance", "metrics"].map(t => (
            <Tabs.Trigger key={t} value={t}
              className={`px-4 py-2 text-sm font-medium border-b-2 capitalize ${tab === t ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="workers">
          <Card padding="none" headerAction={<Button size="sm" onClick={() => setOpen(true)}><Plus className="w-3 h-3" /> Add</Button>}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {["Emp ID", "Name", "Department", "Role", "Skills", "Status"].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[11px] font-semibold uppercase text-slate-600">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {workers.map(w => (
                    <tr key={w.id} className="border-b border-slate-100">
                      <td className="px-3 py-2 font-mono text-xs">{w.employee_id}</td>
                      <td className="px-3 py-2 font-medium">{w.name}</td>
                      <td className="px-3 py-2">{w.department}</td>
                      <td className="px-3 py-2">{w.role}</td>
                      <td className="px-3 py-2">
                        <div className="flex gap-1 flex-wrap">
                          {(w.skills || []).map((s: string, i: number) => (
                            <span key={i} className="px-1.5 py-0.5 text-[10px] bg-blue-50 text-blue-700 rounded">{s}</span>
                          ))}
                        </div>
                      </td>
                      <td className="px-3 py-2"><Badge variant={w.status === "active" ? "success" : "muted"}>{w.status}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="shifts">
          <Card><p className="text-sm text-slate-500 py-6 text-center">Shift assignment grid — coming soon</p></Card>
        </Tabs.Content>

        <Tabs.Content value="attendance">
          <Card title="Today's Attendance">
            <div className="space-y-1.5 max-h-[500px] overflow-y-auto">
              {att.length === 0 ? (
                <div className="text-slate-400 text-sm py-6 text-center">No attendance records for today</div>
              ) : att.map(a => {
                const worker = workers.find(w => w.id === a.worker_id)
                return (
                  <div key={a.id} className="flex items-center justify-between p-2 border border-slate-200 rounded">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-slate-400" />
                      <span className="text-sm font-medium">{worker?.name ?? a.worker_id}</span>
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="text-slate-500">OT: {a.ot_hours}h</span>
                      <Badge variant={a.status === "present" ? "success" : a.status === "absent" ? "danger" : "warning"}>
                        {a.status}
                      </Badge>
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="metrics">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card title="Attendance Trend">
              <LineChart
                data={(metrics?.attendance_trend || []).map((d: any) => ({ date: d.date?.slice(5), Rate: d.value }))}
                xKey="date" lines={[{ key: "Rate", name: "Attendance %", color: "#16A34A" }]} height={220}
              />
            </Card>
            <Card title="OT Hours by Worker (Top 10)">
              <BarChart
                data={(metrics?.ot_by_worker || []).map((w: any) => ({ name: w.name, Hours: w.ot_hours }))}
                xKey="name" bars={[{ key: "Hours", name: "OT Hours", color: "#D97706" }]} height={220}
              />
            </Card>
          </div>
        </Tabs.Content>
      </Tabs.Root>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40" onClick={() => setOpen(false)}>
          <Card className="w-96" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-sm font-semibold mb-3">Add Worker</h3>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <Input label="Emp ID" {...register("employee_id", { required: true })} />
                <Input label="Name"   {...register("name", { required: true })} />
              </div>
              <Input label="Department" {...register("department")} />
              <Input label="Role" {...register("role")} />
              <div>
                <label className="text-xs font-medium text-slate-700 mb-1 block">Skills</label>
                <div className="flex gap-1 mb-1 flex-wrap">
                  {skills.map(s => (
                    <span key={s} className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded flex items-center gap-1">
                      {s}
                      <button type="button" onClick={() => setSkills(skills.filter(x => x !== s))}>×</button>
                    </span>
                  ))}
                </div>
                <Input value={skillInput} onChange={e => setSkillInput(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === "Enter" && skillInput.trim()) {
                      e.preventDefault()
                      setSkills([...skills, skillInput.trim()])
                      setSkillInput("")
                    }
                  }}
                  placeholder="Type and press Enter" />
              </div>
              <Select label="Status" options={[
                { value: "active", label: "Active" },
                { value: "inactive", label: "Inactive" },
                { value: "on_leave", label: "On Leave" },
              ]} {...register("status")} />
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                <Button type="submit">Save</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  )
}
