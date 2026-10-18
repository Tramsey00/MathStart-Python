import type { ReactNode } from "react";
import { Links, Meta, Outlet, Scripts, ScrollRestoration, isRouteErrorResponse, useMatches } from "react-router";
import type { Route } from "./+types/root";
import { SiteShell } from "../shared/ui/site-shell";
import { SkipLink } from "../shared/ui/components";
import siteCss from "../../../static/mathstart/css/site.css?url";
import type { PublicPageView } from "../server/public-types";
import migrationCss from "../public-migration.css?url";

export const links: Route.LinksFunction = () => [{ rel: "stylesheet", href: siteCss }];
export const meta: Route.MetaFunction = () => [{ title: "MathStart" }];

// Keep document Layout identical during fallback and hydration.
export function Layout({ children }: { children: ReactNode }) {
  const view=useMatches().map(m=>m.data).find((d):d is PublicPageView=>!!d && typeof d === "object" && "canonical_url" in d && "page" in d);
  return (
    <html lang="ru">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        {view ? <>
          <title>{view.page.seo.title}</title>
          <meta name="description" content={view.page.seo.description}/>
          <meta name="robots" content="index, follow"/>
          <link rel="canonical" href={view.canonical_url}/>
          <meta property="og:site_name" content="MathStart"/>
          <meta property="og:title" content={view.page.seo.title}/>
          <meta property="og:description" content={view.page.seo.description}/>
          <meta property="og:url" content={view.canonical_url}/>
          <meta property="og:locale" content="ru_RU"/>
          <meta property="og:type" content={view.page.page_type === "topic" ? "article" : "website"}/>
          <meta name="twitter:card" content="summary"/>
          {view.page.assets.filter(a=>a.kind === "style").map(a=><link key={a.url} rel="stylesheet" href={a.url}/>)}
          <link rel="stylesheet" href={migrationCss}/>
        </> : <><Meta/><Links/></>}
      </head>
      <body>
        {children}
        {view?.page.assets.filter(a=>a.kind === "script").map(a=><script key={a.url} src={a.url}/>)}
        <ScrollRestoration/><Scripts/>
      </body>
    </html>
  );
}

export default function App() {
  const skip = useMatches().flatMap(match => {
    const handle = match.handle;
    if (!handle || typeof handle !== "object" || !("skipLink" in handle)) return [];
    const value = handle.skipLink;
    return value && typeof value === "object" && "target" in value && "label" in value
      && typeof value.target === "string" && typeof value.label === "string"
      ? [{target: value.target, label: value.label}] : [];
  }).at(-1);
  return <SiteShell skipLink={skip ? <SkipLink target={skip.target}>{skip.label}</SkipLink> : undefined}><Outlet /></SiteShell>;
}

// Build-time shell has no user/session/API state.
export function HydrateFallback() {
  return <SiteShell><main id="main-content" tabIndex={-1} aria-busy="true" /></SiteShell>;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  const missing = isRouteErrorResponse(error) && error.status === 404;
  return <SiteShell><main id="main-content" tabIndex={-1}><h1>{missing ? "Страница не найдена" : "Не удалось открыть страницу"}</h1></main></SiteShell>;
}
