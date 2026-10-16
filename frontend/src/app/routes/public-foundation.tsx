import { useLoaderData } from "react-router";
import { loadPublicPage } from "../../server/public-input.server";
import type { PublicPageView } from "../../server/public-types";

export const handle = { publicDocument: true };
export async function loader({request}:{request:Request}) {
  // The framework builds the private SPA shell at the home URL. That shell
  // must render the same empty root layout that hydrates on a private path.
  if(request.headers.get('X-React-Router-SPA-Mode') === 'yes') return null;
  return loadPublicPage(new URL(request.url).pathname);
}

// Reviewed HTML is publication output. Complete document navigation disposes
// authored scripts, observers, timers and styles. Public pages never hydrate.
export function LessonHost({view}:{view:PublicPageView}) {
  return <>
    <div data-lesson-host="" data-public-slug={view.page.slug} style={{display:"contents"}} dangerouslySetInnerHTML={{__html:view.page.body_html}}/>
    {view.catalogue_html !== null && <section data-mathstart-catalogue="" className="ms-catalogue" dangerouslySetInnerHTML={{__html:view.catalogue_html}}/>}
    {view.catalogue_html !== null && <template data-mathstart-catalogue-end=""/>}
  </>;
}
export default function PublicPage() {
  return <LessonHost view={useLoaderData<PublicPageView>()}/>;
}
