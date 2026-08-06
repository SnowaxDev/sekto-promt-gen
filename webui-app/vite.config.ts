import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

// The workspace talks to the FastAPI backend (default http://127.0.0.1:8000).
// In dev we proxy the JSON endpoints so there are no CORS surprises.
const API_PATHS = [
  "/prompt", "/brief", "/generate", "/refine", "/series", "/rate", "/best",
  "/leaderboard", "/generations", "/knowledge", "/patterns", "/variant", "/usage",
];

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  server: {
    port: 5173,
    proxy: Object.fromEntries(
      API_PATHS.map((p) => [p, { target: "http://127.0.0.1:8000", changeOrigin: true }])
    ),
  },
});
