export const APP_NAME        = "EMICP"
export const APP_VERSION     = "1.0.0"
export const APP_TAGLINE     = "One Platform. All Factories. One Decision."
export const API_BASE_URL    = "http://127.0.0.1:37210/api/v1"
export const BACKEND_PORT    = 37210
export const BACKEND_HEALTH  = "http://127.0.0.1:37210/health"
export const HEALTH_INTERVAL = 2000
export const PAGE_SIZE       = 20

export const FACTORY_TYPES = [
  { value: "b2b",    label: "B2B — Business to Business" },
  { value: "b2c",    label: "B2C — Business to Consumer" },
  { value: "hybrid", label: "Hybrid — B2B + B2C"         },
]

export const CURRENCIES = [
  { value: "USD", label: "USD — US Dollar"     },
  { value: "EUR", label: "EUR — Euro"           },
  { value: "SAR", label: "SAR — Saudi Riyal"   },
  { value: "AED", label: "AED — UAE Dirham"    },
  { value: "GBP", label: "GBP — British Pound" },
  { value: "EGP", label: "EGP — Egyptian Pound"},
]

export const STATUS_COLORS: Record<string, string> = {
  active:      "bg-green-100 text-green-700",
  inactive:    "bg-gray-100 text-gray-600",
  maintenance: "bg-yellow-100 text-yellow-700",
  down:        "bg-red-100 text-red-700",
  running:     "bg-green-100 text-green-700",
  idle:        "bg-yellow-100 text-yellow-700",
  planned:     "bg-blue-100 text-blue-700",
  completed:   "bg-green-100 text-green-700",
  cancelled:   "bg-red-100 text-red-700",
}

export const SEVERITY_COLORS: Record<string, string> = {
  info:      "bg-blue-50 text-blue-700 border-blue-200",
  warning:   "bg-yellow-50 text-yellow-700 border-yellow-200",
  critical:  "bg-red-50 text-red-700 border-red-200",
  emergency: "bg-red-100 text-red-900 border-red-400",
}

export const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
