import type { Config } from "@react-router/dev/config";
import { readFileSync } from "node:fs";
const input = process.env.MATHSTART_PUBLIC_VIEW;
const paths = input ? Object.keys(JSON.parse(readFileSync(input, "utf8")).routes) : [];

// I02 adds validated published URLs only; never prerender account/admin.
export default {
  appDirectory: "src/app",
  buildDirectory: process.env.MATHSTART_ROUTER_BUILD || "build",
  ssr: false,
  routeDiscovery: { mode: 'initial' },
  prerender: paths,
  future: { v8_trailingSlashAwareDataRequests: true },
} satisfies Config;
