"""Materialize the reviewed Django oracle only for explicit comparisons.

The application never calls this module. The checkout is a detached local clone
of a literal commit, not a download or a floating ref. Historical requirements,
settings, templates and probes are used directly from that checkout.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ORACLE_SHA = '1a87b044e8c5a7519b0ab57e22d2a35d57b4a986'
DEFAULT_CHECKOUT = ROOT / 'var' / 'legacy-oracle' / ORACLE_SHA


def git(root, *arguments):
    return subprocess.check_output(['git', '-c', 'safe.directory=' + str(root),
                                    '-C', str(root), *arguments], stderr=subprocess.PIPE,
                                   timeout=120).decode('utf-8').strip()


def oracle_root():
    supplied = Path(os.environ.get('MATHSTART_LEGACY_CHECKOUT', DEFAULT_CHECKOUT))
    path = supplied.resolve()
    if path == ROOT or not path.is_relative_to(ROOT / 'var') or supplied.is_symlink():
        raise RuntimeError('Oracle must be a separate checkout under this repository var/')
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        git(ROOT, 'cat-file', '-e', ORACLE_SHA + '^{commit}')
        # A Windows sandbox account can read this user-owned linked worktree.
        # Trust only its verified exact metadata directory for this command;
        # never change global safe.directory or trust a wildcard.
        source_gitdir = git(ROOT, 'rev-parse', '--absolute-git-dir')
        clone_env = dict(os.environ)
        count = int(clone_env.get('GIT_CONFIG_COUNT', '0'))
        clone_env.update({'GIT_CONFIG_COUNT': str(count + 1),
                          f'GIT_CONFIG_KEY_{count}': 'safe.directory',
                          f'GIT_CONFIG_VALUE_{count}': source_gitdir})
        subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--no-checkout',
                        '--no-hardlinks', '--local', str(ROOT), str(path)],
                       env=clone_env, check=True, capture_output=True, timeout=120)
        git(path, 'config', 'core.autocrlf', 'false')
        git(path, 'config', 'core.longpaths', 'true')
        git(path, 'checkout', '--detach', ORACLE_SHA)
    if (git(path, 'rev-parse', '--show-toplevel').replace('\\', '/') != path.as_posix()
            or git(path, 'rev-parse', 'HEAD') != ORACLE_SHA
            or git(path, 'status', '--porcelain', '--untracked-files=all')):
        raise RuntimeError('Oracle checkout must be pristine and match the pinned SHA')
    # Historical rollback-only asset probes use TemporaryDirectory(dir='var').
    # This is ignored oracle runtime, never an authored or target source copy.
    (path / 'var').mkdir(exist_ok=True)
    return path


def legacy_python():
    configured = os.environ.get('MATHSTART_LEGACY_PYTHON')
    if not configured:
        raise RuntimeError('Explicit separate legacy fixture interpreter required')
    path = Path(configured).absolute()  # Do not dereference POSIX venv links.
    if not path.is_file() or path == Path(sys.executable).absolute():
        raise RuntimeError('Separate installed legacy interpreter required')
    return str(path)


def oracle_environment(environment=None):
    env = dict(os.environ if environment is None else environment)
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    env['PYTHONNOUSERSITE'] = '1'
    return env


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--run', nargs=argparse.REMAINDER,
                        help='Explicit historical Python arguments, e.g. manage.py check')
    args = parser.parse_args(argv)
    root = oracle_root()
    if args.run:
        return subprocess.call([legacy_python(), *args.run], cwd=root, env=oracle_environment())
    print(root)
    print('Pinned oracle SHA: ' + ORACLE_SHA)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
