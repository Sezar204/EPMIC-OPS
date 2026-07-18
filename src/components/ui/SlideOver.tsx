Input
import { ReactNode } from "react"
import * as Dialog from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { cn } from "@/utils/cn"

interface Props {
  open: boolean
  onClose: () => void
  title?: string
  subtitle?: string
  size?: "sm" | "md" | "lg"
  children: ReactNode
  footer?: ReactNode
}

const SIZE = { sm: "max-w-[480px]", md: "max-w-[640px]", lg: "max-w-[800px]" }

export function SlideOver({ open, onClose, title, subtitle, size = "md", children, footer }: Props) {
  return (
    <Dialog.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40 z-50 animate-fade-in" />
        <Dialog.Content
          className={cn(
            "fixed right-0 top-0 h-full w-full bg-white z-50 shadow-2xl",
            "flex flex-col border-l border-slate-200",
            "animate-in slide-in-from-right duration-300",
            SIZE[size]
          )}
        >
          <div className="flex items-start justify-between px-5 py-4 border-b border-slate-200 flex-shrink-0">
            <div>
              {title    && <Dialog.Title className="text-base font-semibold text-slate-900">{title}</Dialog.Title>}
              {subtitle && <Dialog.Description className="text-xs text-slate-500 mt-1">{subtitle}</Dialog.Description>}
            </div>
            <Dialog.Close asChild>
              <button className="text-slate-400 hover:text-slate-700 p-1 rounded">
                <X className="w-4 h-4" />
              </button>
            </Dialog.Close>
          </div>
          <div className="flex-1 overflow-y-auto p-5">{children}</div>
          {footer && (
            <div className="px-5 py-3 border-t border-slate-200 flex items-center justify-end gap-2 flex-shrink-0">
              {footer}
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

export default SlideOver
