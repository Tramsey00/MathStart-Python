import {beforeEach, describe, expect, it, vi} from "vitest";
import {createHash} from "node:crypto";
import {resolve} from "node:path";
const fixtures = vi.hoisted(() => ({files: new Map<string, Buffer>(), blobs: new Map<string, Buffer>()}));
vi.mock("node:fs", () => { const api = {
  readFileSync: (path: string, encoding?: string) => {
    const raw = fixtures.files.get(String(path));
    if (!raw) throw new Error("Missing fixture file");
    return encoding ? raw.toString() : raw;
  },
  existsSync: (path: string) => fixtures.files.has(String(path)),
}; return {...api, default: api}; });
vi.mock("node:child_process", () => { const api = {execFileSync: (_command: string, args: string[]) => {
  const raw = fixtures.blobs.get(args[1] ?? "");
  if (!raw) throw new Error("Missing Git fixture blob");
  return raw;
}}; return {...api, default: api}; });
import {preservedContract} from "../scripts/preserved-contracts.mjs";
const root = resolve(".cache/preservation-unit-fixture");
const source = "1a87b044e8c5a7519b0ab57e22d2a35d57b4a986";
const sha = (raw: Buffer) => createHash("sha256").update(raw).digest("hex");
const original = Buffer.from("original reviewed source\n");
const updated = Buffer.from("explicit current platform adapter\n");
function manifest(files: object[]) {
  fixtures.files.set(resolve(root, "specs/migration/post-django-preservation.json"), Buffer.from(JSON.stringify({
    source_sha: source, accepted_input: "8d958aeeb17da46839722441425ccbb5889e2ab7", files,
  })));
}
beforeEach(() => {fixtures.files.clear(); fixtures.blobs.clear();});
describe("preservation during contract generation", () => {
  it("compares retained contracts to their actual current working bytes", () => {
    manifest([]);
    fixtures.blobs.set("HEAD:retained.json", original);
    fixtures.files.set(resolve(root, "retained.json"), original);
    expect(preservedContract(root, "retained.json")).toEqual(original);
    fixtures.files.set(resolve(root, "retained.json"), Buffer.from("unknown edit"));
    expect(() => preservedContract(root, "retained.json")).toThrow("working copy changed");
  });
  it("keeps original digest while requiring both current HEAD and reviewed working adapter", () => {
    manifest([{path: "adapter.py", action: "updated", sha256: sha(original), bytes: original.length,
      current_sha256: sha(updated)}]);
    fixtures.blobs.set(source + ":adapter.py", original);
    fixtures.blobs.set("HEAD:adapter.py", updated);
    fixtures.files.set(resolve(root, "adapter.py"), updated);
    expect(preservedContract(root, "adapter.py")).toEqual(original);
    fixtures.blobs.set("HEAD:adapter.py", original);
    expect(() => preservedContract(root, "adapter.py")).toThrow("Unreviewed current adapter");
    fixtures.blobs.set("HEAD:adapter.py", updated);
    fixtures.files.set(resolve(root, "adapter.py"), original);
    expect(() => preservedContract(root, "adapter.py")).toThrow("Unreviewed current adapter");
  });
  it("rejects reintroduced retired paths and altered historical provenance", () => {
    manifest([{path: "retired.py", action: "removed", sha256: sha(original), bytes: original.length}]);
    fixtures.blobs.set(source + ":retired.py", original);
    expect(preservedContract(root, "retired.py")).toEqual(original);
    fixtures.files.set(resolve(root, "retired.py"), original);
    expect(() => preservedContract(root, "retired.py")).toThrow("reintroduced");
    fixtures.files.delete(resolve(root, "retired.py"));
    fixtures.blobs.set(source + ":retired.py", updated);
    expect(() => preservedContract(root, "retired.py")).toThrow("Historical source mismatch");
  });
});
