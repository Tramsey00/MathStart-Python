import type { Config } from "@react-router/dev/config";
import { readFileSync } from "node:fs";
const input = process.env.MATHSTART_PUBLIC_VIEW;
const paths = input ? Object.keys(JSON.parse(readFileSync(input, "utf8")).routes) : [];

// I02 adds validated published URLs only; never prerender account/admin.
export default {
  appDirectory: "src/app",
  buildDirectory: process.env.MATHSTART_ROUTER_BUILD || "build",
  // Render wildcard errors at the requested URL in host-dev. The release
  // build still emits static public documents and a private SPA shell.
  ssr: process.env.MATHSTART_DEV_MODE === '1',
  routeDiscovery: { mode: 'initial' },
  prerender: input ? [...paths, "/404"] : paths,
  future: { v8_trailingSlashAwareDataRequests: true },
} satisfies Config;
