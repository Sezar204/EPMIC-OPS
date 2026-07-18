Input
export function PageSkeleton() {
  return (
    <div className="page-container animate-fade-in">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="h-6 w-48 skeleton" />
            <div className="h-3 w-64 skeleton mt-2" />
          </div>
          <div className="flex gap-2">
            <div className="h-9 w-24 skeleton" />
            <div className="h-9 w-32 skeleton" />
          </div>
        </div>

        {/* Stat cards row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div className="w-10 h-10 rounded-lg skeleton" />
                <div className="h-3 w-12 skeleton" />
              </div>
              <div>
                <div className="h-3 w-20 skeleton" />
                <div className="h-6 w-24 skeleton mt-2" />
              </div>
            </div>
          ))}
        </div>

        {/* Table skeleton */}
        <div className="card">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <div className="h-4 w-32 skeleton" />
            <div className="h-9 w-48 skeleton" />
          </div>
          <div className="p-4 space-y-2">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-9 skeleton" />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PageSkeleton
