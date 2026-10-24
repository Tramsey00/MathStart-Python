export interface PublicPageView {
  public_design?: 'home' | 'catalogue';
  public_catalogue?: import('../features/public-pages/catalogue-context').PublicCatalogue;
  page:{id:string;slug:string;page_type:string;title:string;body_html:string;
    source?: { path: string };
    renderer_version?: 'legacy' | 'react-v1';
    lesson_document?: import('../shared/lesson/lesson-types').LessonDocument;
    seo:{title:string;description:string;canonical_path:string};
    assets:{url:string;kind:"style"|"script"|"media";lifecycle:string;sha256:string;order:number}[]};
  canonical_url:string;
  catalogue_html:string|null;
  context:{pinned_release:{release_id:string;manifest_digest:string};
    lesson_navigation?: import('../shared/lesson/lesson-page').LessonPageNavigation;
    lesson_section?: {title:string;href:string};
    grade_links?: {title:string;href:string}[]};
}
