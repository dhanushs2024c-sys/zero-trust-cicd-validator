/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        zt: {
          bg: "#0B0F19",
          card: "#111827",
          border: "#1F2937",
          hover: "#1E293B",
          accent: "#06B6D4",
          success: "#10B981",
          danger: "#EF4444",
          warning: "#F59E0B",
          muted: "#94A3B8"
        }
      }
    },
  },
  plugins: [],
}
