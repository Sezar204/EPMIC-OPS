Input
import { useState, useMemo, ReactNode } from "react"
import {
  ColumnDef, flexRender, getCoreRowModel, getSortedRowModel,
  getFilteredRowModel, getPaginationRowModel, useReactTable,
  SortingState, ColumnFiltersState,
} from "@tanstack/react-table"
import { ChevronUp, ChevronDown, Search, Inbox } from "lucide-react"
import { cn } from "@/utils/cn"
import { Input } from "./Input"
import { Button } from "./Button"

interface Props<T> {
  data: T[]
  columns: ColumnDef<T, unknown>[]
  isLoading?: boolean
  emptyMessage?: string
  emptyIcon?: ReactNode
  onRowClick?: (row: T) => void
  searchPlaceholder?: string
  showSearch?: boolean
  pageSize?: number
  stickyHeader?: boolean
}

export function Table<T>({
  data, columns, isLoading, emptyMessage = "No data found",
  emptyIcon, onRowClick, searchPlaceholder = "Search...",
  showSearch = true, pageSize = 20, stickyHeader = true,
}: Props<T>) {
  const [sorting, setSorting]         = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter]   = useState("")

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, globalFilter },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel:    getCoreRowModel(),
    getSortedRowModel:  getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize } },
  })

  const totalRows = table.getFilteredRowModel().rows.length
  const pageIndex = table.getState().pagination.pageIndex
  const pageCount = table.getPageCount()

  return (
    <div className="w-full">
      {showSearch && (
        <div className="mb-3 max-w-xs">
          <Input
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder={searchPlaceholder}
            leftIcon={<Search className="w-3.5 h-3.5" />}
          />
        </div>
      )}

      <div className={cn("border border-slate-200 rounded-lg overflow-hidden bg-white", stickyHeader && "max-h-[60vh]")}>
        <div className="overflow-auto max-h-full">
          <table className="w-full text-sm">
            <thead className={cn("bg-slate-50 border-b border-slate-200", stickyHeader && "sticky top-0 z-10")}>
              {table.getHeaderGroups().map((hg) => (
                <tr key={hg.id}>
                  {hg.headers.map((h) => {
                    const canSort = h.column.getCanSort()
                    const sorted  = h.column.getIsSorted()
                    return (
                      <th
                        key={h.id}
                        className={cn(
                          "px-3 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-600",
                          canSort && "cursor-pointer select-none hover:bg-slate-100"
                        )}
                        onClick={canSort ? h.column.getToggleSortingHandler() : undefined}
                      >
                        <div className="flex items-center gap-1">
                          {flexRender(h.column.columnDef.header, h.getContext())}
                          {sorted === "asc"  && <ChevronUp   className="w-3 h-3" />}
                          {sorted === "desc" && <ChevronDown className="w-3 h-3" />}
                        </div>
                      </th>
                    )
                  })}
                </tr>
              ))}
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="border-b border-slate-100">
                    {columns.map((_, j) => (
                      <td key={j} className="px-3 py-3"><div className="h-4 skeleton" /></td>
                    ))}
                  </tr>
                ))
              ) : table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="py-12 text-center">
                    <div className="flex flex-col items-center gap-2 text-slate-400">
                      {emptyIcon || <Inbox className="w-10 h-10" />}
                      <p className="text-sm">{emptyMessage}</p>
                    </div>
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    onClick={onRowClick ? () => onRowClick(row.original) : undefined}
                    className={cn(
                      "border-b border-slate-100 hover:bg-slate-50 transition-colors",
                      onRowClick && "cursor-pointer"
                    )}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-3 py-2.5 text-slate-700">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {totalRows > pageSize && (
        <div className="flex items-center justify-between mt-3 text-xs text-slate-600">
          <div>
            Showing {pageIndex * pageSize + 1}–
            {Math.min((pageIndex + 1) * pageSize, totalRows)} of {totalRows}
          </div>
          <div className="flex items-center gap-1">
            <Button size="sm" variant="outline" disabled={!table.getCanPreviousPage()}
              onClick={() => table.previousPage()}>Prev</Button>
            <span className="px-2">Page {pageIndex + 1} / {pageCount}</span>
            <Button size="sm" variant="outline" disabled={!table.getCanNextPage()}
              onClick={() => table.nextPage()}>Next</Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Table
