"""Target disposable upgrade wrapper; owner-reviewed rehearsal is mandatory."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.target_check import main as run_check


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disposable", action="store_true", required=True)
    parser.add_argument("--source-profile", choices=("A", "B", "C"), required=True)
    args = parser.parse_args(argv)
    return run_check(["upgrade-" + args.source_profile, "--disposable"])


if __name__ == "__main__":
    raise SystemExit(main())
