import { readFileSync } from "node:fs";
import type { PublicPageView } from "./public-types";
type Projection = { release_id: string; manifest_digest: string; routes: Record<string, PublicPageView> };
let projection: { input: string; data: Projection } | undefined;

export async function loadPublicPage(path:string):Promise<PublicPageView> {
  const input=process.env.MATHSTART_PUBLIC_VIEW;
  if(!input) throw new Response("Verified publication input required",{status:503});
  // The projection is process-local and prepared before startup or build.
  // The editable lesson document is still read separately for each HMR load.
  if (projection?.input !== input) {
    projection = { input, data: JSON.parse(readFileSync(input, "utf8")) as Projection };
  }
  const data = projection.data;
  if (!Object.hasOwn(data.routes, path)) throw new Response("Unknown publication page", {status:404});
  const view = data.routes[path]!;
  if (view.context.pinned_release.release_id!==data.release_id || view.context.pinned_release.manifest_digest!==data.manifest_digest)
    throw new Response("Publication projection does not match its pin",{status:503});
  if (import.meta.env.DEV && process.env.MATHSTART_DEV_MODE === '1') {
    const { currentLessonView } = await import('./dev-public-input.server');
    return currentLessonView(view);
  }
  return view;
}
