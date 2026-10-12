"""Fresh/upgrade/check CLI smoke in a target-only venv where Django is absent."""
import json
import os
from pathlib import Path
import subprocess
from backend.tests.test_postgres import PostgreSQLTests


def main():
    interpreter = Path('var/ms7-mig-v01-runtime-venv/Scripts/python.exe').resolve()
    checks = []
    PostgreSQLTests.setUpClass()
    try:
        for profile in (None, None, 'A', 'B', 'C'):
            with PostgreSQLTests().database(profile) as engine:
                if profile: PostgreSQLTests().seed(engine, profile)
                env = {**os.environ, 'MATHSTART_DB_BACKEND': 'postgresql',
                       'MATHSTART_DATABASE_URL': engine.url.render_as_string(hide_password=False)}
                arguments = ['fresh','--disposable'] if not profile else ['upgrade','--profile',profile,'--disposable','--reviewed-rehearsal']
                for command in (arguments, ['check','--disposable']):
                    code = ('import importlib.util,sys; assert importlib.util.find_spec("django") is None; '
                            'from backend.migrate import main; result=main(' + repr(command) + '); '
                            'assert not any(m=="django" or m.startswith("django.") for m in sys.modules); '
                            'raise SystemExit(result)')
                    process = subprocess.run([str(interpreter), '-c', code], env=env, capture_output=True)
                    result = {'profile': profile or 'FRESH', 'command': command, 'exit_code': process.returncode,
                              'Django_installed_or_imported': False,
                              'safe_output': process.stdout.decode(errors='replace').strip()}
                    checks.append(result)
                    print((profile or 'FRESH') + ' ' + command[0] + ': exit ' + str(process.returncode), flush=True)
                    if process.returncode:
                        raise RuntimeError('Target-only runtime smoke failed: '+process.stderr.decode(errors='replace')[-1200:])
    finally:
        PostgreSQLTests.tearDownClass()
        directory = Path(os.environ.get('MATHSTART_V01_EVIDENCE_DIR', 'var/ms7-mig-v01-evidence'))
        directory.mkdir(parents=True, exist_ok=True)
        (directory / 'runtime-verification.json').write_text(
            json.dumps({'status': 'PASS' if len(checks) == 10 and all(c['exit_code'] == 0 for c in checks) else 'FAIL',
                        'runtime_dependency_lock': 'backend/requirements.lock', 'checks': checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
