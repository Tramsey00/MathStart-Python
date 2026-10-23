export type MaterialAddress = Readonly<{ grade: number; subject: string; number: number }>;
export type MaterialRoute = MaterialAddress & Readonly<{ slug: string; path: string }>;
export function buildMaterialPath(address: MaterialAddress): string;
export function materialPathForSlug(slug: string): string | undefined;
export const materialRoutes: readonly MaterialRoute[];
export const quadraticRoute: MaterialRoute;
