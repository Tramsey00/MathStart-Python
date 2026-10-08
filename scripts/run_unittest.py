"""Nonempty, unskipped unittest execution. Missing tests cannot return empty PASS."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True)
    parser.add_argument("--pattern", required=True)
    args = parser.parse_args(argv)
    start = (ROOT / args.start).resolve()
    if not start.is_relative_to(ROOT) or not start.is_dir():
        print("FAIL: test directory missing or outside checkout.")
        return 1
    # Keep the product Harness package ahead of tests/harness during discovery.
    if str(start) not in sys.path:
        sys.path.append(str(start))
    suite = unittest.defaultTestLoader.discover(str(start), pattern=args.pattern)
    if suite.countTestCases() == 0:
        print("FAIL: required suite contains zero tests.")
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.skipped:
        print("FAIL: skipped tests cannot establish required evidence.")
    return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__ == "__main__":
    raise SystemExit(main())
