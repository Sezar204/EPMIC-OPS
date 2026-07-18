Input
import * as AlertDialog from "@radix-ui/react-alert-dialog"
import { AlertTriangle } from "lucide-react"
import { Button } from "./Button"

interface Props {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  danger?: boolean
}

export function ConfirmDialog({
  open, onClose, onConfirm, title, message,
  confirmLabel = "Confirm", cancelLabel = "Cancel", danger = false,
}: Props) {
  return (
    <AlertDialog.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="fixed inset-0 bg-black/40 z-50 animate-fade-in" />
        <AlertDialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-[90vw] max-w-md bg-white rounded-xl shadow-2xl p-5 animate-fade-in">
          <div className="flex gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${danger ? "bg-red-100" : "bg-blue-100"}`}>
              <AlertTriangle className={`w-5 h-5 ${danger ? "text-danger" : "text-primary"}`} />
            </div>
            <div className="flex-1 min-w-0">
              <AlertDialog.Title className="text-base font-semibold text-slate-900">
                {title}
              </AlertDialog.Title>
              <AlertDialog.Description className="text-sm text-slate-600 mt-1">
                {message}
              </AlertDialog.Description>
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-5">
            <AlertDialog.Cancel asChild>
              <Button variant="outline" size="sm" onClick={onClose}>{cancelLabel}</Button>
            </AlertDialog.Cancel>
            <AlertDialog.Action asChild>
              <Button
                variant={danger ? "danger" : "default"}
                size="sm"
                onClick={() => { onConfirm(); onClose() }}
              >
                {confirmLabel}
              </Button>
            </AlertDialog.Action>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  )
}

export default ConfirmDialog
