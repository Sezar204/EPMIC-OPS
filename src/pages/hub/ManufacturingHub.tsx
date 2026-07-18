import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Building2, ArrowRight, BarChart3 } from "lucide-react"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { PageSkeleton } from "@/components/ui/PageSkeleton"
import { useAppStore } from "@/stores/appStore"
export default function ManufacturingHub() {
  const navigate = useNavigate(); const factories = useAppStore((s) => s.factories); const setCurrentFactory = useAppStore((s) => s.setCurrentFactory); const backendReady = useAppStore((s) => s.backendReady)
  useEffect(() => { if (factories.length === 1 && !useAppStore.getState().currentFactory) setCurrentFactory(factories[0]) }, [factories, setCurrentFactory])
  if (!backendReady) return <PageSkeleton />
  const openFactory = (id: number) => { const factory = factories.find((item) => item.id === id); if (factory) { setCurrentFactory(factory); navigate("/factory/" + id + "/dashboard") } }
  return <div className="page-container"><div className="flex items-start justify-between mb-6"><div><h1 className="text-2xl font-bold">Manufacturing Hub</h1><p className="text-slate-500 mt-1">Choose a factory to review its live operations and decisions.</p></div><Button variant="outline" leftIcon={<BarChart3 className="w-4 h-4" />} onClick={() => navigate("/corporate")}>Corporate Center</Button></div><div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">{factories.map((factory) => <Card key={factory.id} className="hover:shadow-md transition-shadow"><div className="flex items-start justify-between"><div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center"><Building2 className="w-5 h-5" /></div><span className="px-2 py-1 rounded text-xs bg-green-100 text-green-700">{factory.status}</span></div><h2 className="font-semibold text-slate-900 mt-4">{factory.name}</h2><p className="text-xs text-slate-500 mt-1">{factory.code} · {factory.location || "Location not set"}</p><Button className="w-full mt-4" variant="outline" rightIcon={<ArrowRight className="w-4 h-4" />} onClick={() => openFactory(factory.id)}>Open Factory</Button></Card>)}</div>{!factories.length && <Card><p className="text-slate-500">No factories are available. Start the backend to load the seeded workspace.</p></Card>}</div>
}

