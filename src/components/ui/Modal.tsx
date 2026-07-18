Input
import { ReactNode } from "react"
import * as Dialog from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { cn } from "@/utils/cn"

interface Props {
  open: boolean
  onClose: () => void
  title?: string
  description?: string
  size?: "sm" | "md" | "lg" | "xl"
  children: ReactNode
  footer?: ReactNode
}

const SIZE = { sm: "max-w-sm", md: "max-w-md", lg: "max-w-2xl", xl: "max-w-4xl" }

export function Modal({ open, onClose, title, description, size = "md", children, footer }: Props) {
  return (
    <Dialog.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 animate-fade-in" />
        <Dialog.Content
          className={cn(
            "fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50",
            "w-[95vw] bg-white rounded-xl shadow-2xl border border-slate-200",
            "max-h-[90vh] flex flex-col animate-fade-in",
            SIZE[size]
          )}
        >
          {(title || description) && (
            <div className="flex items-start justify-between px-5 py-4 border-b border-slate-200">
              <div>
                {title && <Dialog.Title className="text-base font-semibold text-slate-900">{title}</Dialog.Title>}
                {description && <Dialog.Description className="text-xs text-slate-500 mt-1">{description}</Dialog.Description>}
              </div>
              <Dialog.Close asChild>
                <button className="text-slate-400 hover:text-slate-700 p-1 rounded">
                  <X className="w-4 h-4" />
                </button>
              </Dialog.Close>
            </div>
          )}
          <div className="flex-1 overflow-y-auto p-5">{children}</div>
          {footer && (
            <div className="px-5 py-3 border-t border-slate-200 flex items-center justify-end gap-2">
              {footer}
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

export default Modal
