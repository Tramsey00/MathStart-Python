// Current contracts stay current; only explicit post-Django dispositions read
// historical Git bytes. Original manifest digests are never regenerated.
import {readFileSync, existsSync} from "node:fs";
import {resolve} from "node:path";
import {execFileSync} from "node:child_process";
import {createHash} from "node:crypto";
const source = "1a87b044e8c5a7519b0ab57e22d2a35d57b4a986";
const maintenanceSource = "3a290a46d991e22269a17dde41e39f0637576071";
const hash = raw => createHash("sha256").update(raw).digest("hex");
export function preservedContract(root, path) {
  const manifest = JSON.parse(readFileSync(resolve(root, "specs/migration/post-django-preservation.json"), "utf8"));
  if (manifest.source_sha !== source || manifest.accepted_input !== "8d958aeeb17da46839722441425ccbb5889e2ab7")
    throw new Error("Unexpected contract provenance");
  const row = manifest.files.find(row => row.path === path);
  const pin = row?.source_sha ?? source;
  if (row && pin !== source && pin !== maintenanceSource) throw new Error("Unreviewed historical source");
  const blob = execFileSync("git", ["show", (row ? pin : "HEAD") + ":" + path], {cwd: root});
  if (row) {
    if (hash(blob) !== row.sha256 || blob.length !== row.bytes) throw new Error("Historical source mismatch: " + path);
    if (row.action === "updated") {
      if (hash(readFileSync(resolve(root, path))) !== row.current_sha256 ||
          hash(execFileSync("git", ["show", "HEAD:" + path], {cwd: root})) !== row.current_sha256)
        throw new Error("Unreviewed current adapter: " + path);
    } else if (["removed", "moved", "moved_updated"].includes(row.action)) {
      if (existsSync(resolve(root, path))) throw new Error("Retired source reintroduced: " + path);
      if (row.action === "moved" && hash(readFileSync(resolve(root, row.destination))) !== row.sha256)
        throw new Error("Shared extraction changed: " + path);
      if (row.action === "moved_updated" && hash(readFileSync(resolve(root, row.destination))) !== row.current_sha256)
        throw new Error("Unreviewed moved adapter: " + path);
    } else throw new Error("Unknown preservation disposition");
  } else if (readFileSync(resolve(root, path), "utf8").replace(/\r\n/g, "\n") !== blob.toString("utf8").replace(/\r\n/g, "\n")) {
    throw new Error("Contract working copy changed: " + path);
  }
  return blob;
}
