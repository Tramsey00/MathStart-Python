import { index, layout, route, type RouteConfig } from "@react-router/dev/routes";
import { debugRoutesEnabled } from "./route-foundation";
export default [
  layout("layouts/public.tsx",[
    index("routes/public-foundation.tsx"),
    route("karta-sajta/","routes/public-foundation.tsx",{id:"catalogue-foundation"}),
    route("o-proekte/","routes/public-foundation.tsx",{id:"about-foundation"}),
    route("kontakty/","routes/public-foundation.tsx",{id:"contact-foundation"}),
  ]),
  layout("layouts/account.tsx",[route("account/","routes/account-foundation.tsx")]),
  layout("layouts/staff.tsx",[route("admin/","routes/staff-foundation.tsx")]),
  ...(debugRoutesEnabled(process.env.NODE_ENV)?[
    layout("layouts/debug.tsx",[route("__ui__/foundation/","routes/foundation-gallery.tsx")]),
  ]:[]),
] satisfies RouteConfig;
