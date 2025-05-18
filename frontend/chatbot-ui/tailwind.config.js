/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      colors: {
        primary: {
          light: "#6366f1",
          DEFAULT: "#4f46e5",
          dark: "#4338ca",
        },
        secondary: {
          light: "#f3f4f6",
          DEFAULT: "#e5e7eb",
          dark: "#d1d5db",
        },
        accent: {
          light: "#93c5fd",
          DEFAULT: "#60a5fa",
          dark: "#3b82f6",
        },
        background: {
          light: "#ffffff",
          DEFAULT: "#f9fafb",
          dark: "#f3f4f6",
        },
        surface: {
          light: "#ffffff",
          DEFAULT: "#ffffff",
          dark: "#f9fafb",
        },
        error: {
          light: "#ef4444",
          DEFAULT: "#dc2626",
          dark: "#b91c1c",
        },
        success: {
          light: "#10b981",
          DEFAULT: "#059669",
          dark: "#047857",
        },
        warning: {
          light: "#f59e0b",
          DEFAULT: "#d97706",
          dark: "#b45309",
        },
        info: {
          light: "#3b82f6",
          DEFAULT: "#2563eb",
          dark: "#1d4ed8",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["Fira Code", "monospace"],
      },
      boxShadow: {
        chat: "0 0 15px rgba(0, 0, 0, 0.1)",
        message: "0 2px 5px rgba(0, 0, 0, 0.05)",
      },
      borderRadius: {
        message: "1.5rem",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "bounce-slow": "bounce 2s infinite",
        typing: "typing 1.5s infinite",
      },
      keyframes: {
        typing: {
          "0%": { opacity: 0.3 },
          "50%": { opacity: 1 },
          "100%": { opacity: 0.3 },
        },
      },
    },
  },
  plugins: [],
};
