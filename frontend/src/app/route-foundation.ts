export const foundationPaths = ["/", "/materials", "/o-proekte/", "/kontakty/", "/account/", "/admin/"] as const;
export const debugFoundationPath = "/__ui__/foundation/";

export function debugRoutesEnabled(environment: string | undefined): boolean {
  return environment === "development";
}
