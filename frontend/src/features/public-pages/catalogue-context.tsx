import { createContext, useContext, type ReactNode } from 'react';
export interface CatalogueItem { title: string; slug: string; order: number; description?: string }
export interface CatalogueSubject extends CatalogueItem { grade: string }
export interface CatalogueSection extends CatalogueSubject { subject: string }
export interface CatalogueTopic extends CatalogueSection { section: string; url: string }
export interface PublicCatalogue { grades: CatalogueItem[]; subjects: CatalogueSubject[]; sections: CatalogueSection[]; topics: CatalogueTopic[] }
const Context = createContext<PublicCatalogue | null>(null);
export function PublicCatalogueProvider({ catalogue, children }: { catalogue: PublicCatalogue; children: ReactNode }) {
  return <Context.Provider value={catalogue}>{children}</Context.Provider>;
}
export function useCatalogue() { const value = useContext(Context); if (!value) throw Error('Published catalogue required'); return value; }
