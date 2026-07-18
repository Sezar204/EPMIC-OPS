import * as Dialog from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { cn } from "@/utils/cn"

interface ModalProps {
  open: boolean
  onClose: () => void
  title?: string
  description?: string
  size?: "sm" | "md" | "lg" | "xl"
  children: React.ReactNode
  footer?: React.ReactNode
}

const sizeMap = { sm: "max-w-sm", md: "max-w-lg", lg: "max-w-2xl", xl: "max-w-4xl" }

export function Modal({ open, onClose, title, description, size = "md", children, footer }: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={(o) => { if (!o) onClose() }}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40 z-50 animate-fade-in" />
        <Dialog.Content
          className={cn(
            "fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full bg-white rounded-xl shadow-xl flex flex-col max-h-[90vh]",
            sizeMap[size]
          )}
        >
          <div className="flex items-start justify-between px-5 py-4 border-b border-border">
            <div>
              {title && <Dialog.Title className="text-base font-semibold text-slate-900">{title}</Dialog.Title>}
              {description && <Dialog.Description className="text-xs text-slate-500 mt-1">{description}</Dialog.Description>}
            </div>
            <Dialog.Close className="text-slate-400 hover:text-slate-700 transition">
              <X className="w-5 h-5" />
            </Dialog.Close>
          </div>
          <div className="px-5 py-4 overflow-y-auto flex-1">{children}</div>
          {footer && (
            <div className="px-5 py-3 border-t border-border flex justify-end gap-2">{footer}</div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
