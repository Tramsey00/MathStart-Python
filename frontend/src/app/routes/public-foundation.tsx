import { useLoaderData } from "react-router";
import { loadPublicPage } from "../../server/public-input.server";
import type { PublicPageView } from "../../server/public-types";
import { LessonPage } from '../../shared/lesson/lesson-page';
import { PublicDesignHost } from '../../features/public-pages/public-design-host';

export const handle = { publicDocument: true };
export async function loader({request}:{request:Request}) {
  // The framework builds the private SPA shell at the home URL. That shell
  // must render the same empty root layout that hydrates on a private path.
  if(request.headers.get('X-React-Router-SPA-Mode') === 'yes') return null;
  return loadPublicPage(new URL(request.url).pathname);
}

// Legacy HTML keeps its full-document lifecycle. Approved public pages and
// react-v1 lessons hydrate their shared React components from publication data.
export function LessonHost({view}:{view:PublicPageView}) {
  if (view.public_design) {
    if (!view.public_catalogue) throw Error('Published catalogue required');
    return <PublicDesignHost kind={view.public_design} catalogue={view.public_catalogue} fallback={view.catalogue_html}/>;
  }
  if (view.page.renderer_version === 'react-v1') {
    if (!view.page.lesson_document || !view.context.lesson_navigation || !view.context.grade_links || !view.context.lesson_section) throw Error('Incomplete React lesson publication');
    return <LessonPage document={view.page.lesson_document} navigation={view.context.lesson_navigation} gradeLinks={view.context.grade_links} section={view.context.lesson_section}/>;
  }
  const authored=<div data-lesson-host="" data-public-slug={view.page.slug} style={{display:"contents"}} dangerouslySetInnerHTML={{__html:view.page.body_html}}/>;
  if(view.catalogue_html === null)return authored;
  return <main className="ms-catalogue" id="topics-catalogue">
    {authored}
    <section data-mathstart-catalogue="" className="ms-catalogue" dangerouslySetInnerHTML={{__html:view.catalogue_html}}/>
    <template data-mathstart-catalogue-end=""/>
  </main>;
}
export default function PublicPage() {
  return <LessonHost view={useLoaderData<PublicPageView>()}/>;
}
