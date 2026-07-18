import { useState } from "react"
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table"
import { ChevronUp, ChevronDown, ChevronsUpDown, Search } from "lucide-react"
import { cn } from "@/utils/cn"
import { PAGE_SIZE } from "@/constants"
import { EmptyState } from "./EmptyState"

interface TableProps<T> {
  data: T[]
  columns: ColumnDef<T, any>[]
  isLoading?: boolean
  emptyMessage?: string
  emptyAction?: () => void
  emptyActionLabel?: string
  onRowClick?: (row: T) => void
  searchable?: boolean
  initialPageSize?: number
}

export function Table<T>({
  data,
  columns,
  isLoading,
  emptyMessage = "No records found",
  emptyAction,
  emptyActionLabel,
  onRowClick,
  searchable,
  initialPageSize = PAGE_SIZE,
}: TableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([])
  const [globalFilter, setGlobalFilter] = useState("")

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: "includesString",
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: initialPageSize } },
  })

  if (isLoading) {
    return (
      <div className="card overflow-hidden">
        <div className="p-3 border-b border-border">
          <div className="skeleton h-8 w-64" />
        </div>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="px-4 py-3 border-b border-border flex gap-4">
            <div className="skeleton h-4 flex-1" />
            <div className="skeleton h-4 w-24" />
            <div className="skeleton h-4 w-16" />
          </div>
        ))}
      </div>
    )
  }

  if (!data.length) {
    return <EmptyState title={emptyMessage} actionLabel={emptyActionLabel} onAction={emptyAction} />
  }

  return (
    <div className="card overflow-hidden">
      {searchable && (
        <div className="p-3 border-b border-border">
          <div className="relative w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              value={globalFilter}
              onChange={(e) => setGlobalFilter(e.target.value)}
              placeholder="Search..."
              className="w-full h-9 pl-9 pr-3 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 sticky top-0 z-10">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-2.5 text-left font-semibold text-slate-600 whitespace-nowrap"
                  >
                    {header.isPlaceholder ? null : (
                      <button
                        className="inline-flex items-center gap-1 hover:text-slate-900"
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() &&
                          (header.column.getIsSorted() === "asc" ? (
                            <ChevronUp className="w-3.5 h-3.5" />
                          ) : header.column.getIsSorted() === "desc" ? (
                            <ChevronDown className="w-3.5 h-3.5" />
                          ) : (
                            <ChevronsUpDown className="w-3.5 h-3.5 text-slate-300" />
                          ))}
                      </button>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                onClick={() => onRowClick?.(row.original)}
                className={cn(
                  "border-t border-border hover:bg-slate-50 transition-colors",
                  onRowClick && "cursor-pointer"
                )}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-2.5 text-slate-700 whitespace-nowrap">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between px-4 py-2.5 border-t border-border text-xs text-slate-500">
        <span>
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount() || 1}
          {" "}· {data.length} rows
        </span>
        <div className="flex items-center gap-1">
          <button
            className="px-2 py-1 rounded border border-border hover:bg-slate-50 disabled:opacity-40"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Prev
          </button>
          <button
            className="px-2 py-1 rounded border border-border hover:bg-slate-50 disabled:opacity-40"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
