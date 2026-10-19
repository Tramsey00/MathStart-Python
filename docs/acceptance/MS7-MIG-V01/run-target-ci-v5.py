"""Proposed R03 explicit target CI gate. Not invoked by legacy discovery.

This evidence-only helper is not an applied workflow change.
Requires an explicitly owned disposable PostgreSQL 16 service on reserved port.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
IMPLEMENTATION = "1f97d762c4089efb2e4ef6d8c7ebe0bdcbe161f4"
MODULES = ["backend.tests.test_unit", "backend.tests.test_postgres", "backend.tests.test_remediation"]


def flattened(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flattened(item)
        else:
            yield item


def main():
    expected = os.environ.get("MATHSTART_V01_EXPECTED_HEAD")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if not expected or head != expected:
        raise RuntimeError("Exact candidate HEAD missing or differs; R03 must record actual PR checkout HEAD")
    if subprocess.check_output(["git", "diff", IMPLEMENTATION, head, "--", "backend"], cwd=ROOT):
        raise RuntimeError("Backend changed since reviewed implementation; repeat implementation verification")
    if subprocess.check_output(["git", "status", "--porcelain", "--", "backend"], cwd=ROOT):
        raise RuntimeError("Backend working tree is modified")
    if os.environ.get("MATHSTART_V01_DISPOSABLE_ACK") != "OWNED_DISPOSABLE_POSTGRES_16":
        raise RuntimeError("R03 must supply its isolated disposable PostgreSQL 16 service")
    url = urlsplit(os.environ.get("MATHSTART_V01_TEST_ADMIN_URL", ""))
    if (url.scheme, url.hostname, url.port, url.path) != ("postgresql+psycopg", "127.0.0.1", 55441, "/postgres"):
        raise RuntimeError("Refusing missing, unreserved or shared database endpoint")
    # Explicit loading imports real modules; ImportError/loader errors are never skipped.
    sys.path.insert(0, str(ROOT))
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(MODULES)
    cases = list(flattened(suite))
    ids = [case.id() for case in cases]
    pg = [i for i in ids if i.startswith((MODULES[1] + ".", MODULES[2] + "."))]
    if loader.errors or len(cases) != 34 or len(set(ids)) != 34 or len(pg) != 23:
        raise RuntimeError("FAIL: explicit suite must collect 34 unique cases, including 23 PostgreSQL cases")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    ok = (result.wasSuccessful() and result.testsRun == 34 and not result.skipped
          and not result.expectedFailures and not result.unexpectedSuccesses)
    print(f"V01_TARGET: HEAD={head} implementation={IMPLEMENTATION} "
          f"tests={result.testsRun} PG_collected={len(pg)} skips={len(result.skipped)} "
          f"failures={len(result.failures)} errors={len(result.errors)} status={'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
