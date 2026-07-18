Input
import { ReactNode } from "react"
import { TitleBar }  from "@/components/desktop/TitleBar"
import { StatusBar } from "@/components/desktop/StatusBar"
import { Sidebar }   from "./Sidebar"
import { Notification } from "@/components/ui/Notification"
import { useAppStore }  from "@/stores/appStore"

interface Props { children: ReactNode }

export function AppShell({ children }: Props) {
  const factory       = useAppStore((s) => s.currentFactory)
  const sidebarCollap = useAppStore((s) => s.sidebarCollapsed)

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background">
      <TitleBar />
      <div className="flex-1 flex overflow-hidden">
        {factory && <Sidebar collapsed={sidebarCollap} />}
        <main className="flex-1 overflow-hidden bg-background">
          {children}
        </main>
      </div>
      <StatusBar />
      <Notification />
    </div>
  )
}

export default AppShell
