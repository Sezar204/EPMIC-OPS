Input
import { useEffect, useState } from "react"
import { Search, X } from "lucide-react"
import { Input } from "./Input"

interface Props {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  debounceMs?: number
}

export function SearchBar({ value, onChange, placeholder = "Search...", debounceMs = 300 }: Props) {
  const [local, setLocal] = useState(value)

  useEffect(() => { setLocal(value) }, [value])

  useEffect(() => {
    const t = setTimeout(() => {
      if (local !== value) onChange(local)
    }, debounceMs)
    return () => clearTimeout(t)
  }, [local, debounceMs, onChange, value])

  return (
    <Input
      value={local}
      onChange={(e) => setLocal(e.target.value)}
      placeholder={placeholder}
      leftIcon={<Search className="w-3.5 h-3.5" />}
      rightIcon={
        local ? (
          <button onClick={() => { setLocal(""); onChange("") }} className="text-slate-400 hover:text-slate-700">
            <X className="w-3.5 h-3.5" />
          </button>
        ) : null
      }
    />
  )
}

export default SearchBar
