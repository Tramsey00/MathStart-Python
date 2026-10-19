import { execFileSync } from "node:child_process";
import { fileURLToPath, URL as NodeURL } from "node:url";

// Controlled source-derived reference, NOT a running Django/DB parity assertion.
export function shellReferenceHtml() {
  let html = execFileSync("git", ["show", "1a87b044e8c5a7519b0ab57e22d2a35d57b4a986:templates/base.html"], {cwd: fileURLToPath(new NodeURL("../../", import.meta.url)), encoding: "utf8"});
  const css = fileURLToPath(new NodeURL("../../static/mathstart/css/site.css", import.meta.url)).replaceAll("\\", "/");
  html = html.replace("{% load static %}", "")
    .replace(/\{% block head %\}[\s\S]*?\{% endblock %\}/, "<title>MathStart</title>")
    .replace(/\{% block (skip_link|content|scripts) %\}[\s\S]*?\{% endblock %\}/g, "")
    .replace("{% static 'mathstart/css/site.css' %}", "/@fs/" + css)
    .replace("{% url 'users_ui:account' %}", "/account/");
  if (html.includes("{%") || html.includes("{{")) throw new Error("Unmapped Django template directive");
  return html.replace("</body>", '<script>document.documentElement.dataset.i01BrowserUserAgent = navigator.userAgent; navigator.userAgentData?.getHighEntropyValues([\"fullVersionList\"]).then(value => { document.documentElement.dataset.i01BrowserFullVersions = JSON.stringify(value.fullVersionList); });</script></body>');
}

export function shellReferencePlugin() {
  return {
    name: "mathstart-source-shell-reference",
    apply: "serve",
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        if (request.url !== "/__i01_reference__/shell/") return next();
        response.setHeader("Cache-Control", "no-store");
        response.setHeader("X-Robots-Tag", "noindex, nofollow");
        if (!["GET", "HEAD"].includes(request.method)) {
          response.writeHead(405, {Allow: "GET, HEAD"}).end(); return;
        }
        response.setHeader("Content-Type", "text/html; charset=utf-8");
        response.end(request.method === "HEAD" ? "" : shellReferenceHtml());
      });
    },
  };
}
