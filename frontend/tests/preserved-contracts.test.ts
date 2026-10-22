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
const workflowSource = "1a015f7513933901e8bb252e94c660e4383b6b0e";
function workflow(path: string, before: Buffer, after: Buffer) {
  const data = {base_sha: workflowSource, authority: "explicit user task", files: [{path,
    action: "updated", before_bytes: before.length, before_sha256: sha(before),
    after_sha256: sha(after), reason: "retire unused development runner; keep product checks"}]};
  fixtures.files.set(resolve(root, "specs/maintenance/docs-workflow-dispositions.json"), Buffer.from(JSON.stringify(data)));
  fixtures.blobs.set(workflowSource + ":" + path, before);
  return data;
}
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
  it("pins a relocated adapter to original maintenance blobs and actual new bytes", () => {
    const maintenance = "3a290a46d991e22269a17dde41e39f0637576071";
    manifest([{path: "old/helper.py", source_sha: maintenance, action: "moved_updated",
      destination: "scripts/helper.py", sha256: sha(original), bytes: original.length,
      current_sha256: sha(updated)}]);
    fixtures.blobs.set(maintenance + ":old/helper.py", original);
    fixtures.files.set(resolve(root, "scripts/helper.py"), updated);
    expect(preservedContract(root, "old/helper.py")).toEqual(original);
    fixtures.files.set(resolve(root, "scripts/helper.py"), original);
    expect(() => preservedContract(root, "old/helper.py")).toThrow("Unreviewed moved adapter");
    fixtures.files.set(resolve(root, "scripts/helper.py"), updated);
    fixtures.files.set(resolve(root, "old/helper.py"), original);
    expect(() => preservedContract(root, "old/helper.py")).toThrow("reintroduced");
  });
  it("rejects an unpinned maintenance source before reading historical blobs", () => {
    manifest([{path: "old/helper.py", source_sha: "main", action: "removed",
      sha256: sha(original), bytes: original.length}]);
    expect(() => preservedContract(root, "old/helper.py")).toThrow("Unreviewed historical source");
  });
  it("preserves original approval while checking an explicit subsequent adapter change", () => {
    const next = Buffer.from("current user-authorized CI adapter\n");
    manifest([{path: "adapter.py", action: "updated", sha256: sha(original), bytes: original.length,
      current_sha256: sha(updated)}]);
    fixtures.blobs.set(source + ":adapter.py", original);
    workflow("adapter.py", updated, next);
    fixtures.blobs.set("HEAD:adapter.py", next);
    fixtures.files.set(resolve(root, "adapter.py"), next);
    expect(preservedContract(root, "adapter.py")).toEqual(original);
    fixtures.files.set(resolve(root, "adapter.py"), updated);
    expect(() => preservedContract(root, "adapter.py")).toThrow("Unreviewed current adapter");
    fixtures.files.set(resolve(root, "adapter.py"), next);
    fixtures.blobs.set("HEAD:adapter.py", updated);
    expect(() => preservedContract(root, "adapter.py")).toThrow("Unreviewed current adapter");
  });
  it("rejects a follow-up with a floating source, wrong baseline or altered original bytes", () => {
    manifest([{path: "adapter.py", action: "updated", sha256: sha(original), bytes: original.length,
      current_sha256: sha(updated)}]);
    fixtures.blobs.set(source + ":adapter.py", original);
    const next = Buffer.from("new adapter\n");
    fixtures.blobs.set("HEAD:adapter.py", next);
    fixtures.files.set(resolve(root, "adapter.py"), next);
    const data = workflow("adapter.py", updated, next);
    const mapPath = resolve(root, "specs/maintenance/docs-workflow-dispositions.json");
    data.base_sha = "main";
    fixtures.files.set(mapPath, Buffer.from(JSON.stringify(data)));
    expect(() => preservedContract(root, "adapter.py")).toThrow("Unexpected workflow provenance");
    data.base_sha = workflowSource;
    data.files[0]!.before_sha256 = sha(original);
    fixtures.files.set(mapPath, Buffer.from(JSON.stringify(data)));
    expect(() => preservedContract(root, "adapter.py")).toThrow("Unreviewed workflow input");
    data.files[0]!.before_sha256 = sha(updated);
    fixtures.files.set(mapPath, Buffer.from(JSON.stringify(data)));
    fixtures.blobs.set(workflowSource + ":adapter.py", original);
    expect(() => preservedContract(root, "adapter.py")).toThrow("Workflow original mismatch");
  });
  it("checks a relocated helper's before and after without accepting its retired source", () => {
    const next = Buffer.from("explicit follow-up helper\n");
    manifest([{path: "old/helper.py", action: "moved_updated", destination: "scripts/helper.py",
      sha256: sha(original), bytes: original.length, current_sha256: sha(updated)}]);
    fixtures.blobs.set(source + ":old/helper.py", original);
    workflow("scripts/helper.py", updated, next);
    fixtures.files.set(resolve(root, "scripts/helper.py"), next);
    expect(preservedContract(root, "old/helper.py")).toEqual(original);
    fixtures.files.set(resolve(root, "scripts/helper.py"), updated);
    expect(() => preservedContract(root, "old/helper.py")).toThrow("Unreviewed moved adapter");
    fixtures.files.set(resolve(root, "old/helper.py"), original);
    expect(() => preservedContract(root, "old/helper.py")).toThrow("reintroduced");
  });
});
