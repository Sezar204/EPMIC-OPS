import { useEffect, useState } from "react"
import { Search, X } from "lucide-react"

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export function SearchBar({ value, onChange, placeholder = "Search..." }: SearchBarProps) {
  const [local, setLocal] = useState(value)

  useEffect(() => { setLocal(value) }, [value])

  useEffect(() => {
    const t = setTimeout(() => {
      if (local !== value) onChange(local)
    }, 300)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [local])

  return (
    <div className="relative w-full max-w-sm">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
      <input
        value={local}
        onChange={(e) => setLocal(e.target.value)}
        placeholder={placeholder}
        className="w-full h-9 pl-9 pr-9 rounded-lg border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
      />
      {local && (
        <button
          onClick={() => { setLocal(""); onChange("") }}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}
