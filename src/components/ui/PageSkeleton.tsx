export function PageSkeleton() {
  return (
    <div className="page-container animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div className="skeleton h-8 w-56" />
        <div className="skeleton h-9 w-32" />
      </div>
      <div className="grid grid-cols-4 gap-4 mb-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skeleton h-24 rounded-xl" />
        ))}
      </div>
      <div className="skeleton h-80 w-full rounded-xl" />
    </div>
  )
}
