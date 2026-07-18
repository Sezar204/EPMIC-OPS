import * as Dialog from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { cn } from "@/utils/cn"

interface SlideOverProps {
  open: boolean
  onClose: () => void
  title?: string
  subtitle?: string
  children: React.ReactNode
  footer?: React.ReactNode
}

const widthMap = { sm: "w-[480px]", md: "w-[640px]", lg: "w-[800px]" }

export function SlideOver({
  open,
  onClose,
  title,
  subtitle,
  children,
  footer,
  size = "md",
}: SlideOverProps & { size?: "sm" | "md" | "lg" }) {
  return (
    <Dialog.Root open={open} onOpenChange={(o) => { if (!o) onClose() }}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/30 z-50 animate-fade-in" />
        <Dialog.Content
          className={cn(
            "fixed right-0 top-0 h-full z-50 bg-white shadow-2xl flex flex-col",
            widthMap[size],
            "animate-[fade-in_0.25s_ease-out]"
          )}
        >
          <div className="flex items-start justify-between px-5 py-4 border-b border-border shrink-0">
            <div>
              {title && <Dialog.Title className="text-base font-semibold text-slate-900">{title}</Dialog.Title>}
              {subtitle && <Dialog.Description className="text-xs text-slate-500 mt-1">{subtitle}</Dialog.Description>}
            </div>
            <Dialog.Close className="text-slate-400 hover:text-slate-700 transition">
              <X className="w-5 h-5" />
            </Dialog.Close>
          </div>
          <div className="px-5 py-4 overflow-y-auto flex-1">{children}</div>
          {footer && (
            <div className="px-5 py-3 border-t border-border flex justify-end gap-2 shrink-0">{footer}</div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
