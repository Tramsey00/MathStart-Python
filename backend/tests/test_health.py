"""Real loopback readiness: exact Host, no proxy/redirect or false 503 success."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest
from unittest.mock import patch

from backend.health import ready


@contextmanager
def endpoint(*, status=200, cache='no-cache', body=b'<html><body>ready</body></html>'):
    requests = []
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.path, self.headers.get('Host'), self.headers.get('X-Forwarded-For')))
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', cache)
            self.send_header('Location', '/must-not-follow/')
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port, requests
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
        if thread.is_alive():
            raise RuntimeError('Owned health listener survived cleanup')


class HealthTests(unittest.TestCase):
    def test_real_origin_host_and_no_environment_proxy_or_forwarded_trust(self):
        with endpoint() as (port, requests), patch.dict('os.environ', {'http_proxy': 'http://127.0.0.1:1'}):
            self.assertTrue(ready('https://mathstart.example:8443', port))
        self.assertEqual(requests, [('/', 'mathstart.example:8443', None)])

    def test_redirect_unready_or_incomplete_document_is_never_healthy(self):
        for values in ({'status': 302}, {'status': 503}, {'cache': 'private, no-store'}, {'body': b'<html>partial'}):
            with self.subTest(values=values), endpoint(**values) as (port, requests):
                self.assertFalse(ready('http://localhost', port))
                self.assertEqual(len(requests), 1)

    def test_invalid_config_and_unavailable_listener_fail_bounded(self):
        for origin in ('', 'file:///etc/passwd', 'http://user:password@localhost', 'https://localhost/path', 'https://localhost/?a=b'):
            self.assertFalse(ready(origin, 1))
        self.assertFalse(ready('http://localhost', 0))
        self.assertFalse(ready('http://localhost', 1))


if __name__ == '__main__':
    unittest.main()
