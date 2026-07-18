Input
import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import * as Tabs from "@radix-ui/react-tabs"
import { Save, Database, Info, Calendar, FolderOpen, FileText, Download, Upload } from "lucide-react"
import { format } from "date-fns"
import { useAppStore } from "@/stores/appStore"
import { systemApi, factoriesApi } from "@/api/system"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Select } from "@/components/ui/Select"
import { CURRENCIES, FACTORY_TYPES, APP_NAME, APP_VERSION } from "@/constants"
import { PageSkeleton } from "@/components/ui/PageSkeleton"
import { ConfirmDialog } from "@/components/ui/ConfirmDialog"

export default function Settings() {
  const { factoryId } = useParams<{ factoryId: string }>()
  const fid = Number(factoryId)
  const { notify, setLastBackup } = useAppStore()
  const [tab, setTab] = useState("general")
  const [settings, setSettings] = useState<Record<string, string>>({})
  const [factory, setFactory] = useState<any>(null)
  const [backups, setBackups] = useState<any[]>([])
  const [restoring, setRestoring] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [calMonth, setCalMonth] = useState(new Date())

  useEffect(() => {
    Promise.all([systemApi.getSettings(), factoriesApi.getById(fid), systemApi.listBackups()])
      .then(([s, f, b]) => {
        setSettings((s.data as any) || {})
        setFactory((f as any).data)
        setBackups(((b as any).data as any[]) || [])
        setLoading(false)
      }).catch(() => setLoading(false))
  }, [fid])

  if (loading) return <PageSkeleton />

  const saveSettings = async () => {
    await systemApi.updateSettings(settings)
    notify("Settings saved", "success")
  }
  const saveFactory = async (data: any) => {
    await factoriesApi.update(fid, data)
    notify("Factory updated", "success")
  }
  const backupNow = async () => {
    notify("Creating backup…", "info")
    const r = await systemApi.backupNow()
    setLastBackup((r as any).data.created_at, (r as any).data.status)
    setBackups(((await systemApi.listBackups() as any).data) || [])
    notify("Backup created", "success")
  }
  const restore = async (filename: string) => {
    await systemApi.restoreBackup(filename)
    notify("Restore complete — restart recommended", "success")
    setRestoring(null)
  }

  // Calendar days
  const year  = calMonth.getFullYear()
  const month = calMonth.getMonth()
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const days: (number | null)[] = Array(firstDay).fill(null).concat(Array.from({ length: daysInMonth }, (_, i) => i + 1))

  return (
    <div className="page-container">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Settings</h1>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List className="flex gap-1 border-b border-slate-200 mb-4">
          {[
            { v: "general", l: "General" },
            { v: "factory", l: "Factory" },
            { v: "calendar", l: "Calendar" },
            { v: "backup", l: "Backup" },
            { v: "about", l: "About" },
          ].map(t => (
            <Tabs.Trigger key={t.v} value={t.v}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${tab === t.v ? "border-primary text-primary" : "border-transparent text-slate-500"}`}>
              {t.l}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="general">
          <Card title="General Settings">
            <div className="space-y-3 max-w-md">
              <Select label="Language" options={[
                { value: "en", label: "English" },
                { value: "ar", label: "Arabic (coming soon)" },
              ]} value={settings.language || "en"} onChange={e => setSettings({ ...settings, language: e.target.value })} />
              <Select label="Default Factory" options={[
                { value: String(fid), label: factory?.name ?? `Factory #${fid}` },
              ]} value={String(fid)} disabled />
              <Select label="Theme" options={[
                { value: "light", label: "Light" },
                { value: "dark", label: "Dark (coming soon)" },
              ]} value={settings.theme || "light"} onChange={e => setSettings({ ...settings, theme: e.target.value })} />
              <Button onClick={saveSettings}><Save className="w-4 h-4" /> Save</Button>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="factory">
          {factory && (
            <Card title="Factory Profile" subtitle={factory.code}>
              <div className="grid grid-cols-2 gap-3 max-w-2xl">
                <Input label="Name" defaultValue={factory.name} onChange={e => setFactory({ ...factory, name: e.target.value })} />
                <Select label="Type" options={FACTORY_TYPES} value={factory.type} onChange={e => setFactory({ ...factory, type: e.target.value })} />
                <Input label="Location" defaultValue={factory.location ?? ""} onChange={e => setFactory({ ...factory, location: e.target.value })} />
                <Select label="Currency" options={CURRENCIES} value={factory.currency} onChange={e => setFactory({ ...factory, currency: e.target.value })} />
                <Input label="Working Start" type="time" defaultValue={factory.working_start} onChange={e => setFactory({ ...factory, working_start: e.target.value })} />
                <Input label="Working End"   type="time" defaultValue={factory.working_end}   onChange={e => setFactory({ ...factory, working_end: e.target.value })} />
              </div>
              <div className="mt-3">
                <Button onClick={() => saveFactory(factory)}><Save className="w-4 h-4" /> Update Factory</Button>
              </div>
            </Card>
          )}
        </Tabs.Content>

        <Tabs.Content value="calendar">
          <Card title="Working Calendar" subtitle="Mark holidays and working days">
            <div className="flex items-center gap-2 mb-3">
              <Button size="sm" variant="outline" onClick={() => setCalMonth(new Date(year, month - 1, 1))}>‹</Button>
              <div className="font-semibold">{format(calMonth, "MMMM yyyy")}</div>
              <Button size="sm" variant="outline" onClick={() => setCalMonth(new Date(year, month + 1, 1))}>›</Button>
            </div>
            <div className="grid grid-cols-7 gap-1 text-xs">
              {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(d => (
                <div key={d} className="font-semibold text-center text-slate-600 py-1">{d}</div>
              ))}
              {days.map((d, i) => (
                <div key={i}
                  className={`aspect-square border border-slate-200 rounded p-1 text-center ${d ? "hover:bg-blue-50 cursor-pointer" : ""}`}>
                  {d}
                </div>
              ))}
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="backup">
          <Card title="Backup & Restore" subtitle="Database backups">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <Button onClick={backupNow}><Database className="w-4 h-4" /> Backup Now</Button>
                <div className="text-xs text-slate-500">
                  Auto-backup runs daily at {settings.backup_time || "23:00"}. Keep last {settings.backup_keep || "30"} backups.
                </div>
              </div>

              <div className="border-t border-slate-200 pt-3">
                <h3 className="text-sm font-semibold mb-2">Recent Backups</h3>
                {backups.length === 0 ? (
                  <div className="text-center py-6 text-slate-400 text-sm">No backups yet</div>
                ) : (
                  <div className="space-y-1.5">
                    {backups.map(b => (
                      <div key={b.filename} className="flex items-center justify-between p-2 border border-slate-200 rounded text-xs">
                        <div>
                          <div className="font-mono">{b.filename}</div>
                          <div className="text-slate-500">
                            {b.created_at?.slice(0, 16).replace("T", " ")} · {(b.file_size_bytes / 1024 / 1024).toFixed(2)} MB · {b.backup_type}
                          </div>
                        </div>
                        <Button size="sm" variant="outline" onClick={() => setRestoring(b.filename)}>
                          <Upload className="w-3 h-3" /> Restore
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>
        </Tabs.Content>

        <Tabs.Content value="about">
          <Card title="About">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-slate-500">Application</span><span className="font-semibold">{APP_NAME}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Version</span><span className="font-mono">v{APP_VERSION}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Database</span><span className="font-mono text-xs">emicp.db (SQLite)</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Total Backups</span><span>{backups.length}</span></div>
              <div className="border-t border-slate-200 pt-3 mt-3 flex gap-2">
                <Button variant="outline"><FolderOpen className="w-4 h-4" /> Open App Folder</Button>
                <Button variant="outline"><FileText className="w-4 h-4" /> View Logs</Button>
                <Button variant="outline"><Download className="w-4 h-4" /> Export Data</Button>
              </div>
            </div>
          </Card>
        </Tabs.Content>
      </Tabs.Root>

      <ConfirmDialog
        open={!!restoring}
        onClose={() => setRestoring(null)}
        onConfirm={() => restoring && restore(restoring)}
        title="Restore Database"
        message={`Restore from "${restoring}"? This will overwrite the current database. A safety backup will be created first.`}
        confirmLabel="Restore"
        danger
      />
    </div>
  )
}
