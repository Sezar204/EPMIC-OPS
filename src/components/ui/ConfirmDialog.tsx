import * as AlertDialog from "@radix-ui/react-alert-dialog"
import { Button } from "./Button"

interface ConfirmDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmLabel?: string
  danger?: boolean
  loading?: boolean
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Confirm",
  danger,
  loading,
}: ConfirmDialogProps) {
  return (
    <AlertDialog.Root open={open} onOpenChange={(o) => { if (!o) onClose() }}>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="fixed inset-0 bg-black/40 z-[60] animate-fade-in" />
        <AlertDialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-[60] w-full max-w-sm bg-white rounded-xl shadow-xl p-5">
          <AlertDialog.Title className="text-base font-semibold text-slate-900">{title}</AlertDialog.Title>
          <AlertDialog.Description className="text-sm text-slate-600 mt-2">{message}</AlertDialog.Description>
          <div className="flex justify-end gap-2 mt-5">
            <AlertDialog.Cancel asChild>
              <Button variant="outline" onClick={onClose}>Cancel</Button>
            </AlertDialog.Cancel>
            <AlertDialog.Action asChild>
              <Button variant={danger ? "danger" : "default"} loading={loading} onClick={onConfirm}>
                {confirmLabel}
              </Button>
            </AlertDialog.Action>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  )
}
