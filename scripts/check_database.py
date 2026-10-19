"""Bounded target diagnostic; explicit legacy uses the pinned oracle."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('target', 'legacy'), default='target')
    args = parser.parse_args()
    if args.profile == 'legacy':
        from scripts.legacy_oracle import main as legacy
        return legacy(['--run', 'scripts/check_database.py'])
    from scripts.target_database import main as target
    return target()
if __name__ == '__main__':
    raise SystemExit(main())
