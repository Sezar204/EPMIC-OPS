/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary:    { DEFAULT: "#1E40AF", foreground: "#FFFFFF" },
        secondary:  { DEFAULT: "#0F172A", foreground: "#F8FAFC" },
        success:    { DEFAULT: "#16A34A", light: "#DCFCE7", dark: "#166534" },
        warning:    { DEFAULT: "#D97706", light: "#FEF3C7", dark: "#92400E" },
        danger:     { DEFAULT: "#DC2626", light: "#FEE2E2", dark: "#991B1B" },
        info:       { DEFAULT: "#0891B2", light: "#CFFAFE", dark: "#164E63" },
        background: "#F8FAFC",
        border:     "#E2E8F0",
        muted:      { DEFAULT: "#F1F5F9", foreground: "#64748B" },
        sidebar:    { DEFAULT: "#0F172A", hover: "#1E293B" },
      },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
      borderRadius: { xl: "0.75rem", lg: "0.5rem" },
      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(4px)" },
          to:   { opacity: "1", transform: "translateY(0)"   },
        },
        shimmer: {
          from: { backgroundPosition: "-200px 0" },
          to:   { backgroundPosition: "calc(200px + 100%) 0" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.3s ease-out",
        shimmer:   "shimmer 1.5s infinite linear",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
