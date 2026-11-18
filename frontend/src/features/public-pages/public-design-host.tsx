import { PublicCatalogueProvider, type PublicCatalogue } from './catalogue-context';
import { HomePage } from './home-page';
import { MaterialsPage } from './materials-page';

export function PublicDesignHost({ kind, catalogue, fallback }: { kind: 'home' | 'catalogue'; catalogue: PublicCatalogue; fallback: string | null }) {
  return <PublicCatalogueProvider catalogue={catalogue}><div data-public-design={kind}>
    {kind === 'home' ? <HomePage /> : <>
      <MaterialsPage />
      <noscript className="catalogue-readable-fallback" suppressHydrationWarning
        dangerouslySetInnerHTML={{ __html: '<section data-mathstart-catalogue="" class="ms-catalogue">'
          + (fallback ?? '') + '</section><template data-mathstart-catalogue-end=""></template>' }} />
    </>}
  </div></PublicCatalogueProvider>;
}
