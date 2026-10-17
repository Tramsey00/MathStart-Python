"""Bounded service lifecycle for the I02/I03 real browser checks.

The caller supplies reviewed argv lists and a loopback URL. A pre-existing
listener is never adopted or stopped. Cleanup is required after every outcome.
This helper does not mark any migration task or browser matrix as passing.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
import signal
import socket
import subprocess
import time
from urllib.parse import urlsplit
from urllib.request import urlopen


class LifecycleFailure(RuntimeError):
    pass


def _listening(host, port):
    with socket.socket() as connection:
        connection.settimeout(0.2)
        return connection.connect_ex((host, port)) == 0


def _stop(process):
    if os.name == 'nt':
        try:
            process._public_job.stop()
        except OSError as error:
            raise LifecycleFailure('Owned process job cleanup was refused') from error
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == 'nt':
            process.kill()
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait(timeout=5)


def start_owned_process(argv, **kwargs):
    if os.name != 'nt':
        return subprocess.Popen(argv,start_new_session=True,**kwargs)
    from scripts.windows_job import WindowsJob
    job = WindowsJob()
    process = None
    try:
        process = subprocess.Popen(argv,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | 0x00000004,
                                   **kwargs)  # CREATE_SUSPENDED: assign before any descendants exist.
        process._public_job = job
        job.assign_and_resume(process.pid)
        return process
    except Exception:
        try:
            job.stop()
        finally:
            if process is not None:
                process.kill()
                process.wait(timeout=5)
        raise
@contextmanager
def owned_http_service(server_argv, *, base_url, cwd, evidence_root,
                       environment=None, startup_timeout=30):
    parsed = urlsplit(base_url)
    if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1'
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ('', '/')):
        raise LifecycleFailure('An explicit loopback HTTP origin is required')
    port = parsed.port or 80
    if _listening('127.0.0.1', port):
        raise LifecycleFailure('Reserved port already has a listener')
    root = Path(evidence_root)
    root.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy() if environment is None else dict(environment)
    with (root / 'server.log').open('wb') as server_log:
        process = start_owned_process(server_argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                      stdout=server_log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + startup_timeout
            while True:
                if process.poll() is not None:
                    raise LifecycleFailure('Owned server exited before readiness')
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise LifecycleFailure('Owned server readiness timed out')
                try:
                    # A cold integrity-checked release may take several seconds.
                    # Keep the absolute startup deadline, but do not queue a new
                    # request every 500ms while the previous request still runs.
                    with urlopen(base_url, timeout=min(5, remaining)) as response:
                        ready = response.status == 200
                    if ready:
                        break
                except (OSError, TimeoutError):
                    pass
                if time.monotonic() >= deadline:
                    raise LifecycleFailure('Owned server readiness timed out')
                time.sleep(0.1)
            yield
        finally:
            _stop(process)
            deadline = time.monotonic() + 3
            while _listening('127.0.0.1', port) and time.monotonic() < deadline:
                time.sleep(0.1)
            if _listening('127.0.0.1', port):
                raise LifecycleFailure('Owned server listener survived cleanup')


def run_browser_check(server_argv, check_argv, *, base_url, cwd, evidence_root,
                      environment=None, startup_timeout=30, check_timeout=540):
    env = os.environ.copy() if environment is None else dict(environment)
    env['MATHSTART_E2E_BASE_URL'] = base_url.rstrip('/')
    root = Path(evidence_root)
    result = {'startup': 'NOT_RUN', 'browser_exit': None, 'cleanup': 'NOT_RUN'}
    with owned_http_service(server_argv, base_url=base_url, cwd=cwd, evidence_root=root,
                            environment=env, startup_timeout=startup_timeout):
        result['startup'] = 'PASS'
        with (root / 'browser.log').open('wb') as browser_log:
            check = start_owned_process(check_argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                        stdout=browser_log, stderr=subprocess.STDOUT)
            try:
                result['browser_exit'] = check.wait(timeout=check_timeout)
            finally:
                _stop(check)
    result['cleanup'] = 'PASS'
    return result
