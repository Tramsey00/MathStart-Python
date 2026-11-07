// Current contracts stay current; only explicit post-Django dispositions read
// historical Git bytes. Original manifest digests are never regenerated.
import {readFileSync, existsSync} from "node:fs";
import {resolve} from "node:path";
import {execFileSync} from "node:child_process";
import {createHash} from "node:crypto";
const source = "1a87b044e8c5a7519b0ab57e22d2a35d57b4a986";
const maintenanceSource = "3a290a46d991e22269a17dde41e39f0637576071";
const workflowSource = "1a015f7513933901e8bb252e94c660e4383b6b0e";
const hash = raw => createHash("sha256").update(raw).digest("hex");
const documentationSource = "b29a7ccdd07784cfcfd19278cbe59b30c83cd4ea";
const taskSource = '406995b4005d9b78525f3e985e9345a5437a5e67';
function reviewedTaskChange(root, path) {
  const file = resolve(root, 'specs/maintenance/t001-dispositions.json');
  if (!existsSync(file)) return null;
  const map = JSON.parse(readFileSync(file, 'utf8'));
  if (map.source_commit !== taskSource || map.task !== 'MS-T001' || !map.authority || new Set(map.files.map(r => r.path)).size !== map.files.length) throw Error('Unexpected task provenance');
  const row = map.files.find(r => r.path === path);
  if (!row) return null;
  const original = execFileSync('git', ['show', taskSource + ':' + path], {cwd:root});
  if (row.action !== 'updated' || !row.reason || original.length !== row.before_bytes || hash(original) !== row.before_sha256 || hash(readFileSync(resolve(root,path))) !== row.after_sha256) throw Error('Unreviewed task change: ' + path);
  return {row, original};
}
function reviewedRepositoryChange(root, path) {
  const mapPath = resolve(root, "specs/maintenance/repository-cleanup.json");
  if (!existsSync(mapPath)) return null;
  const map = JSON.parse(readFileSync(mapPath, "utf8"));
  if (map.source_commit !== documentationSource || !map.authority ||
      new Set(map.files.map(row => row.path)).size !== map.files.length)
    throw new Error("Unexpected repository change provenance");
  const row = map.files.find(row => row.path === path);
  if (!row || row.action !== "updated") return null;
  const original = execFileSync("git", ["show", documentationSource + ":" + path], {cwd: root});
  const task = reviewedTaskChange(root, path);
  if (!row.reason || original.length !== row.before_bytes || hash(original) !== row.before_sha256 ||
      (task ? task.row.before_sha256 !== row.after_sha256 : hash(readFileSync(resolve(root, path))) !== row.after_sha256))
    throw new Error("Unreviewed repository change: " + path);
  return {row, original};
}
function currentAdapterHash(root, path, previousHash) {
  const mapPath = resolve(root, "specs/maintenance/docs-workflow-dispositions.json");
  if (!existsSync(mapPath)) return previousHash;
  const map = JSON.parse(readFileSync(mapPath, "utf8"));
  if (map.base_sha !== workflowSource || !map.authority ||
      new Set(map.files.map(row => row.path)).size !== map.files.length)
    throw new Error("Unexpected workflow provenance");
  const followup = map.files.find(row => row.path === path);
  if (!followup) return previousHash;
  if (followup.action !== "updated" || !followup.reason || followup.before_sha256 !== previousHash)
    throw new Error("Unreviewed workflow input: " + path);
  const before = execFileSync("git", ["show", workflowSource + ":" + path], {cwd: root});
  if (hash(before) !== followup.before_sha256 || before.length !== followup.before_bytes)
    throw new Error("Workflow original mismatch: " + path);
  return followup.after_sha256;
}
export function preservedContract(root, path) {
  const task = reviewedTaskChange(root, path);
  const change = reviewedRepositoryChange(root, path);
  const documentation = path.endsWith(".md") ? change?.original : null;
  const manifest = JSON.parse(readFileSync(resolve(root, "specs/migration/post-django-preservation.json"), "utf8"));
  if (manifest.source_sha !== source || manifest.accepted_input !== "8d958aeeb17da46839722441425ccbb5889e2ab7")
    throw new Error("Unexpected contract provenance");
  const row = manifest.files.find(row => row.path === path);
  const pin = row?.source_sha ?? source;
  if (row && pin !== source && pin !== maintenanceSource) throw new Error("Unreviewed historical source");
  const blob = execFileSync("git", ["show", (row ? pin : "HEAD") + ":" + path], {cwd: root});
  if (row) {
    if (hash(blob) !== row.sha256 || blob.length !== row.bytes) throw new Error("Historical source mismatch: " + path);
    if (task) return blob;
    if (documentation) return blob;
    if (row.action === "updated") {
      const current = currentAdapterHash(root, path, row.current_sha256);
      const head = hash(execFileSync("git", ["show", "HEAD:" + path], {cwd: root}));
      if (change) {
        // A named follow-up must continue the prior reviewed chain. Allow the
        // pinned baseline HEAD while reviewing a dirty candidate, or its exact
        // committed result; unrelated HEAD/working edits still fail.
        if (change.row.before_sha256 !== current ||
            ![current, change.row.after_sha256].includes(head))
          throw new Error("Unreviewed current adapter chain: " + path);
      } else if (hash(readFileSync(resolve(root, path))) !== current || head !== current) {
        throw new Error("Unreviewed current adapter: " + path);
      }
    } else if (["removed", "moved", "moved_updated"].includes(row.action)) {
      if (existsSync(resolve(root, path))) throw new Error("Retired source reintroduced: " + path);
      if (row.action === "moved" && hash(readFileSync(resolve(root, row.destination))) !== currentAdapterHash(root, row.destination, row.sha256))
        throw new Error("Shared extraction changed: " + path);
      if (row.action === "moved_updated" && hash(readFileSync(resolve(root, row.destination))) !== currentAdapterHash(root, row.destination, row.current_sha256))
        throw new Error("Unreviewed moved adapter: " + path);
    } else throw new Error("Unknown preservation disposition");
  } else if (task) {
    return task.original;
  } else if (documentation) {
    return documentation;
  } else if (readFileSync(resolve(root, path), "utf8").replace(/\r\n/g, "\n") !== blob.toString("utf8").replace(/\r\n/g, "\n")) {
    throw new Error("Contract working copy changed: " + path);
  }
  return blob;
}
