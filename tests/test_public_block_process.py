"""Real subprocess/HTTP failures must preserve the I02/I03 service boundary."""
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest

from scripts.public_block_process import LifecycleFailure, owned_http_service, run_browser_check


class PublicBlockLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'index.html').write_text('synthetic public readiness', encoding='utf-8')
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0))
            self.port = reservation.getsockname()[1]
        self.origin = f'http://127.0.0.1:{self.port}'
        self.server = [sys.executable, '-m', 'http.server', str(self.port), '--bind', '127.0.0.1']

    def execute(self, server=None, check=None, **options):
        return run_browser_check(server or self.server,
            check or [sys.executable, '-c', 'raise SystemExit(0)'], base_url=self.origin,
            cwd=self.root, evidence_root=self.root / 'evidence', startup_timeout=3,
            check_timeout=3, **options)

    def assert_closed(self):
        with socket.socket() as connection:
            connection.settimeout(0.2)
            self.assertNotEqual(connection.connect_ex(('127.0.0.1', self.port)), 0)

    def test_success_passes_origin_and_stops_its_server(self):
        result = self.execute(check=[sys.executable, '-c',
            "import os,urllib.request; assert urllib.request.urlopen(os.environ['MATHSTART_E2E_BASE_URL']).read()==b'synthetic public readiness'"])
        self.assertEqual(result, {'startup':'PASS','browser_exit':0,'cleanup':'PASS'})
        self.assert_closed()

    def test_explicit_readiness_route_and_origin_escape_refusal(self):
        code = f'''import http.server
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if self.path=='/health.txt' else 503)
        self.end_headers()
http.server.HTTPServer(('127.0.0.1',{self.port}),Handler).serve_forever()
'''
        with owned_http_service([sys.executable, '-c', code], base_url=self.origin, cwd=self.root,
                evidence_root=self.root / 'route', readiness_path='/health.txt', startup_timeout=3):
            with socket.create_connection(('127.0.0.1', self.port), timeout=1):
                pass
        self.assert_closed()
        for path in ('//example.invalid/', 'https://example.invalid/', '/?secret=x', '/#fragment', '/\\elsewhere'):
            with self.subTest(path=path), self.assertRaisesRegex(LifecycleFailure, 'local readiness path'):
                with owned_http_service(self.server, base_url=self.origin, cwd=self.root,
                        evidence_root=self.root / 'must-not-start', readiness_path=path):
                    self.fail('Unsafe readiness path admitted')
        self.assertFalse((self.root / 'must-not-start').exists())

    def delayed_server(self, seconds):
        code = f'''import http.server,time
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep({seconds!r})
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ready')
http.server.HTTPServer(('127.0.0.1',{self.port}),Handler).serve_forever()
'''
        return [sys.executable, '-c', code]

    def test_cold_response_within_startup_budget_is_not_cancelled_every_half_second(self):
        result = self.execute(server=self.delayed_server(.8))
        self.assertEqual(result, {'startup': 'PASS', 'browser_exit': 0, 'cleanup': 'PASS'})
        self.assert_closed()

    def test_hung_readiness_keeps_absolute_deadline_and_never_runs_browser(self):
        with self.assertRaisesRegex(LifecycleFailure, 'readiness timed out'):
            self.execute(server=self.delayed_server(30),
                         check=[sys.executable, '-c', "open('unexpected-browser','w').close()"])
        self.assertFalse((self.root / 'unexpected-browser').exists())
        self.assert_closed()

    def test_nonzero_browser_remains_nonzero_and_server_is_stopped(self):
        result = self.execute(check=[sys.executable, '-c', 'raise SystemExit(7)'])
        self.assertEqual(result['browser_exit'], 7)
        self.assertEqual(result['cleanup'], 'PASS')
        self.assert_closed()

    def test_failed_startup_does_not_run_browser(self):
        with self.assertRaisesRegex(LifecycleFailure, 'exited before readiness'):
            self.execute(server=[sys.executable,'-c','raise SystemExit(8)'],
                check=[sys.executable,'-c',"open('unexpected-browser','w').close()"])
        self.assertFalse((self.root / 'unexpected-browser').exists())
        self.assert_closed()

    def test_browser_timeout_also_stops_owned_server(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            self.execute(check=[sys.executable,'-c','import time; time.sleep(30)'])
        self.assert_closed()

    def test_browser_timeout_stops_its_child_listener(self):
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0))
            child_port = reservation.getsockname()[1]
        child = [sys.executable, '-m', 'http.server', str(child_port), '--bind', '127.0.0.1']
        code = ('import subprocess,time,pathlib; '
                f'subprocess.Popen({child!r}); '
                "pathlib.Path('browser-child-started').write_text('started'); time.sleep(30)")
        with self.assertRaises(subprocess.TimeoutExpired):
            self.execute(check=[sys.executable, '-c', code])
        self.assertTrue((self.root / 'browser-child-started').is_file())
        with socket.socket() as connection:
            connection.settimeout(0.2)
            self.assertNotEqual(connection.connect_ex(('127.0.0.1', child_port)), 0)
        self.assert_closed()

    def completed_wrapper_child(self, exit_code):
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0))
            port = reservation.getsockname()[1]
        child = [sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1']
        code = f'''import pathlib,socket,subprocess,time
subprocess.Popen({child!r})
deadline=time.monotonic()+2
while True:
    try:
        with socket.create_connection(('127.0.0.1',{port}),timeout=.1):break
    except OSError:
        if time.monotonic()>deadline:raise
        time.sleep(.05)
pathlib.Path('completed-wrapper-child').write_text('started')
raise SystemExit({exit_code})
'''
        result = self.execute(check=[sys.executable,'-c',code])
        self.assertEqual(result,{'startup':'PASS','browser_exit':exit_code,'cleanup':'PASS'})
        self.assertTrue((self.root / 'completed-wrapper-child').is_file())
        with socket.socket() as connection:
            connection.settimeout(.2)
            self.assertNotEqual(connection.connect_ex(('127.0.0.1',port)),0)
        self.assert_closed()

    def test_successful_exited_wrapper_does_not_leave_child_listener(self):
        self.completed_wrapper_child(0)

    def test_failed_exited_wrapper_does_not_leave_child_listener(self):
        self.completed_wrapper_child(7)

    def test_existing_listener_is_neither_adopted_nor_stopped(self):
        with socket.socket() as existing:
            existing.bind(('127.0.0.1', self.port))
            existing.listen()
            with self.assertRaisesRegex(LifecycleFailure, 'already has a listener'):
                self.execute()
            self.assertFalse((self.root / 'evidence').exists())
            self.assertEqual(existing.getsockname()[1], self.port)

    def test_nonloopback_origin_refused_before_process_start(self):
        with self.assertRaisesRegex(LifecycleFailure, 'loopback'):
            run_browser_check(self.server, [], base_url='http://example.com',
                cwd=self.root, evidence_root=self.root / 'evidence')
        self.assertFalse((self.root / 'evidence').exists())

    def test_two_owned_origins_are_ready_and_both_cleaned_up(self):
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0))
            other_port = reservation.getsockname()[1]
        other_origin = f'http://127.0.0.1:{other_port}'
        other_server = [sys.executable, '-m', 'http.server', str(other_port), '--bind', '127.0.0.1']
        with owned_http_service(other_server, base_url=other_origin, cwd=self.root,
                                evidence_root=self.root / 'baseline', startup_timeout=3):
            code = ('import urllib.request; '
                    f"assert urllib.request.urlopen({other_origin!r}).status==200; "
                    f"assert urllib.request.urlopen({self.origin!r}).status==200")
            self.assertEqual(self.execute(check=[sys.executable,'-c',code])['browser_exit'], 0)
        self.assert_closed()
        with socket.socket() as connection:
            connection.settimeout(0.2)
            self.assertNotEqual(connection.connect_ex(('127.0.0.1', other_port)), 0)


if __name__ == '__main__':
    unittest.main()
