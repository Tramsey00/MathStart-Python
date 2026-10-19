"""Fresh target schema/bootstrap verification on explicitly owned disposable data."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('target', 'legacy'), default='target')
    parser.add_argument('--disposable', action='store_true', required=True)
    args = parser.parse_args(argv)
    if args.profile == 'legacy':
        from scripts.legacy_oracle import main as legacy
        return legacy(['--run', 'scripts/fresh_install_smoke.py', '--disposable'])
    from scripts.target_check import main as target
    return target(['fresh-install', '--disposable'])
if __name__ == '__main__':
    raise SystemExit(main())
