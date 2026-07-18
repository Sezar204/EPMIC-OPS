import { TitleBar } from "@/components/desktop/TitleBar"
import { StatusBar } from "@/components/desktop/StatusBar"
import { Sidebar } from "./Sidebar"
import { Notification } from "@/components/ui/Notification"
import { useAppStore } from "@/stores/appStore"

export function AppShell({ children }: { children: React.ReactNode }) {
  const currentFactory = useAppStore((s) => s.currentFactory)
  const sidebarCollapsed = useAppStore((s) => s.sidebarCollapsed)

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden">
        {currentFactory && <Sidebar collapsed={sidebarCollapsed} />}
        <main className="flex-1 overflow-hidden">{children}</main>
      </div>
      <StatusBar />
      <Notification />
    </div>
  )
}
