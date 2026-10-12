import type { Config } from "@react-router/dev/config";

// I02 adds validated published URLs only; never prerender account/admin.
export default {
  appDirectory: "src/app",
  buildDirectory: "build",
  ssr: false,
  prerender: [],
} satisfies Config;
