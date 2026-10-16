import { index, layout, route, type RouteConfig } from "@react-router/dev/routes";
import { debugRoutesEnabled } from "./route-foundation";
import { readFileSync } from "node:fs";
const input = process.env.MATHSTART_PUBLIC_VIEW;
const publicPaths: string[] = input ? Object.keys(JSON.parse(readFileSync(input,"utf8")).routes) : ["/","/karta-sajta/","/o-proekte/","/kontakty/"];
export default [
  layout("layouts/public.tsx",[
    ...publicPaths.map((path,i) => path === "/" ? index("routes/public-foundation.tsx",{id:"public-home"}) : route(path.slice(1),"routes/public-foundation.tsx",{id:`public-${i}`})),
  ]),
  layout("layouts/account.tsx",[route("account/","routes/account-foundation.tsx")]),
  layout("layouts/staff.tsx",[route("admin/*","routes/staff-foundation.tsx")]),
  ...(debugRoutesEnabled(process.env.NODE_ENV)?[
    layout("layouts/debug.tsx",[route("__ui__/foundation/","routes/foundation-gallery.tsx")]),
  ]:[]),
] satisfies RouteConfig;
