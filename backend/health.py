"""Readiness through the ordinary local public gateway, with its trusted Host.

No new public endpoint, bypass of publication authority or database writes.
An uninitialized or broken publication stays unready until reconciled.
"""
import argparse
import os
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


def ready(origin, port=8000):
    try:
        trusted = urlsplit(origin)
        if (trusted.scheme not in {'http', 'https'} or not trusted.netloc or trusted.username or trusted.password
                or trusted.path not in {'', '/'} or trusted.query or trusted.fragment
                or type(port) is not int or not 1 <= port <= 65535):
            return False
        # Loopback selects our process; Host preserves the configured public
        # origin. No environment proxy, forwarded header or redirect is trusted.
        from urllib.request import HTTPRedirectHandler
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, request, fp, code, message, headers, new_url):
                return None
        client = build_opener(ProxyHandler({}), NoRedirect())
        request = Request(f'http://127.0.0.1:{port}/', headers={'Host': trusted.netloc, 'Cache-Control': 'no-cache'})
        with client.open(request, timeout=5) as response:
            payload = response.read(1024 * 1024 + 1)
            return (response.status == 200 and response.headers.get('Cache-Control') == 'no-cache'
                    and response.headers.get_content_type() == 'text/html'
                    and len(payload) <= 1024 * 1024 and b'<html' in payload and b'</html>' in payload)
    except (OSError, ValueError):
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args(argv)
    result = ready(os.environ.get('MATHSTART_PUBLIC_ORIGIN', ''), args.port)
    print('READY' if result else 'UNREADY')
    return 0 if result else 1


if __name__ == '__main__':
    raise SystemExit(main())
