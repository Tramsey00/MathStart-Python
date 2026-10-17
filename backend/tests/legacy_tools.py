"""Keep independent historical fixture subprocesses out of the target runtime."""
import importlib.util
import os
from pathlib import Path
import sys


def legacy_python():
    configured = os.environ.get('MATHSTART_LEGACY_PYTHON')
    if not configured:
        # Historical combined test environments remain supported. A target-only
        # interpreter must receive the explicit separate oracle path.
        if importlib.util.find_spec('django') is None:
            raise RuntimeError('Explicit separate legacy fixture interpreter required')
        configured = sys.executable
    path = Path(configured).absolute()  # Preserve POSIX venv invocation symlinks.
    if not path.is_file():
        raise RuntimeError('Legacy fixture interpreter unavailable')
    return str(path)
