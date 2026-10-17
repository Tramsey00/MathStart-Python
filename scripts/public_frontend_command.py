"""Closed frontend argv adapter for an owned repository-root browser lifecycle."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.verify_public_block import npm_command

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in {'test:e2e', 'test:i02'}:
        raise SystemExit('Only the real frontend browser check is allowed')
    raise SystemExit(subprocess.call(npm_command(sys.argv[1]),cwd=ROOT / 'frontend'))
