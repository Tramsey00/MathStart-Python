import { fileURLToPath } from "node:url";
import { reactRouter } from "@react-router/dev/vite";
import { defineConfig } from "vite";
import { productionBoundaryPlugin } from "./scripts/production-boundary.mjs";
import { shellReferencePlugin } from "./scripts/shell-reference.mjs";

export default defineConfig({
  plugins: [shellReferencePlugin(), productionBoundaryPlugin(), reactRouter()],
  server: {
    host: "127.0.0.1",
    port: 5171,
    strictPort: true,
    fs: { allow: [fileURLToPath(new URL("..", import.meta.url))] },
  },
});
