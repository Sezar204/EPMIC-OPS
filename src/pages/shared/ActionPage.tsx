import { useCallback, useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { Play, RefreshCw } from "lucide-react"
import { api } from "@/api/client"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"
import { PageSkeleton } from "@/components/ui/PageSkeleton"
import { useAppStore } from "@/stores/appStore"
interface ApiResult { data?: unknown }
function renderValue(value: unknown): string { return typeof value === "string" ? value : JSON.stringify(value, null, 2) }
export function ActionPage({ title, endpoint, runEndpoint, description }: { title: string; endpoint: string; runEndpoint?: string; description: string }) {
  const { factoryId } = useParams(); const notify = useAppStore((s) => s.notify); const [data, setData] = useState<unknown>(null); const [loading, setLoading] = useState(true); const [running, setRunning] = useState(false)
  const load = useCallback(async () => { if (!factoryId) return; setLoading(true); try { setData((await api.get<ApiResult>("/factories/" + factoryId + "/" + endpoint)).data ?? null) } catch { notify("Unable to load " + title.toLowerCase(), "error") } finally { setLoading(false) } }, [endpoint, factoryId, notify, title])
  useEffect(() => { void load() }, [load])
  const run = async () => { if (!factoryId || !runEndpoint) return; setRunning(true); try { const result = await api.post<ApiResult>("/engines/" + runEndpoint + "/" + factoryId); setData(result.data ?? null); notify("Analysis completed", "success") } catch { notify("Analysis failed", "error") } finally { setRunning(false) } }
  if (loading) return <PageSkeleton />
  return <div className="page-container"><div className="flex items-start justify-between gap-4 mb-5"><div><h1 className="text-xl font-bold">{title}</h1><p className="text-sm text-slate-500 mt-1">{description}</p></div><div className="flex gap-2"><Button variant="outline" leftIcon={<RefreshCw className="w-4 h-4" />} onClick={() => void load()}>Refresh</Button>{runEndpoint && <Button loading={running} leftIcon={<Play className="w-4 h-4" />} onClick={() => void run()}>Run Analysis</Button>}</div></div><Card><pre className="whitespace-pre-wrap break-words text-sm font-mono text-slate-700">{data === null ? "No data available." : renderValue(data)}</pre></Card></div>
}

