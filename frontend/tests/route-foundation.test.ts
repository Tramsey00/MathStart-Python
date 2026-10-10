import { describe, expect, it } from "vitest";
import { foundationPaths, debugRoutesEnabled } from "../src/app/route-foundation";

describe("route foundations", () => {
  it("preserves the native account/admin paths", () => {
    expect(foundationPaths).toContain("/account/");
    expect(foundationPaths).toContain("/admin/");
    expect(foundationPaths).not.toContain("/staff/");
  });
  it("allows debug only in explicit development", () => {
    expect(debugRoutesEnabled("development")).toBe(true);
    for (const environment of ["production", "test", undefined, ""]) expect(debugRoutesEnabled(environment)).toBe(false);
  });
});
