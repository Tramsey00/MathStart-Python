import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { resolve, sep, extname } from "node:path";

// Local artifact verifier only. V05 owns serving/gateway; not a deployment server.
const routes = new Set(["/", "/karta-sajta/", "/o-proekte/", "/kontakty/", "/account/", "/admin/"]);
const types = {".html":"text/html; charset=utf-8", ".js":"text/javascript; charset=utf-8", ".css":"text/css; charset=utf-8", ".svg":"image/svg+xml"};

export function createPreviewServer(directory = fileURLToPath(new URL("../build/client/", import.meta.url))) {
  const root = resolve(directory);
  return createServer(async (req, res) => {
    res.setHeader("Cache-Control", "no-store");
    const path = new URL(req.url, "http://127.0.0.1").pathname;
    const allowed = path === "/account/" ? ["GET"] : ["GET", "HEAD"];
    if (!allowed.includes(req.method)) { res.writeHead(405,{Allow:allowed.join(", ")}).end(); return; }
    let file;
    if (routes.has(path)) file = resolve(root, "index.html");
    else if (/^\/assets\/[a-zA-Z0-9._-]+$/.test(path)) file = resolve(root, "." + path);
    else { res.writeHead(404).end("Not found"); return; }
    if (!file.startsWith(root + sep)) { res.writeHead(404).end(); return; }
    try {
      if (!(await stat(file)).isFile()) { res.writeHead(404).end(); return; }
      res.setHeader("Content-Type", types[extname(file)] || "application/octet-stream");
      res.end(req.method === "HEAD" ? undefined : await readFile(file));
    } catch { res.writeHead(404).end(); }
  });
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  createPreviewServer().listen(5171,"127.0.0.1",()=>console.log("Local build verification: http://127.0.0.1:5171/ (explicit foundation routes only)"));
}
