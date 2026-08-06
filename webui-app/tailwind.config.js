/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // SeknuTo Dark Emerald tokens
        void: "#060D09",
        panel: "#0A1F14",
        panel2: "#0F2C1C",
        raised: "#143823",
        line: "rgba(255,255,255,0.10)",
        greenline: "rgba(63,163,77,0.35)",
        forest: "#1E5A32",
        primary: "#3FA34D",
        bright: "#4FBF5E",
        blade: "#66BB6A",
        yellow: "#FFD54F",
        red: "#D32F2F",
        ink: "#FFFFFF",
        muted: "rgba(255,255,255,0.72)",
        dim: "rgba(255,255,255,0.45)",
      },
      borderRadius: { xl: "14px", "2xl": "20px" },
      boxShadow: { glow: "0 0 40px rgba(63,163,77,0.35)" },
      fontFamily: { sans: ["Inter", "system-ui", "Segoe UI", "sans-serif"] },
    },
  },
  plugins: [],
};
