import { readFileSync } from "node:fs";
import type { PublicPageView } from "./public-types";
export async function loadPublicPage(path:string):Promise<PublicPageView> {
  const input=process.env.MATHSTART_PUBLIC_VIEW;
  if(!input) throw new Response("Verified publication input required",{status:503});
  const data=JSON.parse(readFileSync(input,"utf8"));
  const view=data.routes[path] as PublicPageView|undefined;
  if(!view || view.context.pinned_release.release_id!==data.release_id || view.context.pinned_release.manifest_digest!==data.manifest_digest)
    throw new Response("Unknown publication page",{status:404});
  if (import.meta.env.DEV && process.env.MATHSTART_DEV_MODE === '1') {
    const { currentLessonView } = await import('./dev-public-input.server');
    return currentLessonView(view);
  }
  return view;
}
