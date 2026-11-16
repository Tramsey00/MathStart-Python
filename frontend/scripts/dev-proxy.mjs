import { readFileSync } from 'node:fs';

export function developmentServerOptions(environment) {
  if (environment.MATHSTART_DEV_MODE !== '1') return {};
  const origin = new URL(environment.MATHSTART_DEV_ORIGIN);
  const backend = new URL(environment.MATHSTART_DEV_API_ORIGIN);
  for (const url of [origin, backend]) {
    if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || !url.port || url.pathname !== '/' || url.search || url.hash || url.username || url.password) {
      throw Error('Development requires explicit loopback origins');
    }
  }
  if (origin.port === backend.port) throw Error('Development frontend/backend ports must differ');
  const view = JSON.parse(readFileSync(environment.MATHSTART_PUBLIC_VIEW, 'utf8'));
  const escape = value => RegExp.escape(value);
  const proxy = { '^/(?:api|_content|static|media|assets)(?:/|\\?|$)': { target: backend.origin, changeOrigin: false } };
  // Documents use the current React routes/HMR. The explicit read below still
  // reaches the existing private HTML adapter for fresh, server-owned hints.
  proxy['^/admin(?:/|\\?|$)'] = { target: backend.origin, changeOrigin: false,
    bypass(request, response) {
      if (['GET', 'HEAD'].includes(request.method) && request.headers['x-mathstart-staff-presentation'] !== '1') {
        response.setHeader('Cache-Control', 'private, no-store');
        response.setHeader('X-Robots-Tag', 'noindex, nofollow');
        response.setHeader('Referrer-Policy', 'no-referrer');
        return request.url;
      }
    } };
  const paths = view.backend_paths ?? [];
  if (paths.length) proxy['^(?:' + paths.map(escape).join('|') + ')(?:\\?|$)'] = { target: backend.origin, changeOrigin: false };
  return {
    port: Number(origin.port), strictPort: true,
    ...(environment.MATHSTART_DEV_CONTAINER === '1' ? { watch: { usePolling: true, interval: 250 } } : {}),
    hmr: { host: origin.hostname, clientPort: Number(origin.port), protocol: 'ws' },
    cors: { origin: origin.origin },
    headers: { 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow', 'Referrer-Policy':'no-referrer' },
    proxy,
  };
}

export function developmentContentPlugin(environment) {
  return {
    name: 'mathstart-dev-content-refresh', apply: 'serve',
    configureServer(server) {
      if (environment.MATHSTART_DEV_MODE !== '1') return;
      const view = JSON.parse(readFileSync(environment.MATHSTART_PUBLIC_VIEW, 'utf8'));
      const paths = view.dev_content_paths ?? [];
      server.watcher.add(paths);
      server.watcher.on('change', path => {
        if (paths.some(source => source.replaceAll('\\', '/') === path.replaceAll('\\', '/'))) {
          server.ws.send({ type: 'full-reload', path: '*' });
        }
      });
    },
  };
}
