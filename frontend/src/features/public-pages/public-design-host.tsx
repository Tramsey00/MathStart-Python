import { useEffect, useState } from 'react';
import { PublicCatalogueProvider, type PublicCatalogue } from './catalogue-context';
import { HomePage } from './home-page';
import { MaterialsPage } from './materials-page';

export function PublicDesignHost({ kind, catalogue, fallback }: { kind: 'home' | 'catalogue'; catalogue: PublicCatalogue; fallback: string | null }) {
  const [enhanced, setEnhanced] = useState(false);
  useEffect(() => setEnhanced(true), []);
  return <PublicCatalogueProvider catalogue={catalogue}><div data-public-design={kind}>
    {kind === 'home' ? <HomePage/> : <>
      <MaterialsPage/>
      <div className="catalogue-readable-fallback" hidden={enhanced}>
        <section data-mathstart-catalogue="" className="ms-catalogue" dangerouslySetInnerHTML={{ __html: fallback ?? '' }}/>
        <template data-mathstart-catalogue-end=""/>
      </div>
    </>}
  </div></PublicCatalogueProvider>;
}
