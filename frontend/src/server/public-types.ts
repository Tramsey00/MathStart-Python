export interface PublicPageView {
  page:{id:string;slug:string;page_type:string;title:string;body_html:string;
    seo:{title:string;description:string;canonical_path:string};
    assets:{url:string;kind:"style"|"script"|"media";lifecycle:string;sha256:string;order:number}[]};
  canonical_url:string;
  catalogue_html:string|null;
  context:{pinned_release:{release_id:string;manifest_digest:string}};
}
