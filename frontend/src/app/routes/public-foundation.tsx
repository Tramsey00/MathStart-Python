import { useLoaderData } from "react-router";
import type { Route } from './+types/public-foundation';
import { loadPublicPage } from "../../server/public-input.server";
import type { PublicPageView } from "../../server/public-types";
import { LessonPage } from '../../shared/lesson/lesson-page';
import { PublicDesignHost } from '../../features/public-pages/public-design-host';

export const handle = { publicDocument: true };
export async function loader({request}:{request:Request}) {
  // The framework builds the private SPA shell at the home URL. That shell
  // must render the same empty root layout that hydrates on a private path.
  if(request.headers.get('X-React-Router-SPA-Mode') === 'yes') return null;
  const view = await loadPublicPage(new URL(request.url).pathname);
  if (!view.public_design && view.page.renderer_version !== 'react-v1' && !isInformationPage(view)) {
    throw new Response('Unknown public page', { status: 404 });
  }
  return view;
}

export function clientLoader({ request, serverLoader }: Route.ClientLoaderArgs) {
  // React Router also matches case-sensitive literal routes with an optional
  // trailing slash. The public site uses each published spelling exactly.
  const path = new URL(request.url).pathname;
  const materials = path === '/materials' || path.startsWith('/materials/');
  if (materials ? path.endsWith('/') : !path.endsWith('/')) {
    throw new Response('Unknown public page', { status: 404 });
  }
  return serverLoader();
}

function isInformationPage(view: PublicPageView) {
  const { page_type, slug, seo } = view.page;
  return page_type === 'static' && (slug === 'o-proekte' || slug === 'kontakty') && seo.canonical_path === `/${slug}/`;
}

export default function PublicPage() {
  const view = useLoaderData<PublicPageView>();
  if (view.public_design) {
    if (!view.public_catalogue) throw Error('Published catalogue required');
    return <PublicDesignHost kind={view.public_design} catalogue={view.public_catalogue} fallback={view.catalogue_html}/>;
  }
  if (view.page.renderer_version === 'react-v1') {
    if (!view.page.lesson_document || !view.context.lesson_navigation || !view.context.grade_links || !view.context.lesson_section) throw Error('Incomplete React lesson publication');
    return <LessonPage document={view.page.lesson_document} navigation={view.context.lesson_navigation} gradeLinks={view.context.grade_links} section={view.context.lesson_section} path={view.page.seo.canonical_path}/>;
  }
  return <div style={{ display: 'contents' }} dangerouslySetInnerHTML={{ __html: view.page.body_html }} />;
}
