"""Legacy CI discovery boundary, independent of SQLAlchemy and Alembic."""
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
BLOCK_TARGET_IMPORTS = '''
import importlib.abc
import sys
attempts = []
class MissingTargetDependencies(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'sqlalchemy', 'alembic'}:
            attempts.append(fullname)
            raise ModuleNotFoundError("No module named %r" % fullname, name=fullname)
sys.meta_path.insert(0, MissingTargetDependencies())
'''


class LegacyDiscoveryTests(unittest.TestCase):
    def run_python(self, code):
        env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'config.settings',
               'DJANGO_DB_BACKEND': 'sqlite', 'DJANGO_DB_PATH': ':memory:',
               'DJANGO_SECRET_KEY': 'synthetic-discovery-only'}
        return subprocess.run([sys.executable, '-c', BLOCK_TARGET_IMPORTS + textwrap.dedent(code)],
                              cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)

    def test_default_django_discovery_preserves_legacy_without_target_imports(self):
        result = self.run_python('''
            import django
            django.setup()
            import unittest
            from django.test.runner import DiscoverRunner, iter_test_cases
            runner = DiscoverRunner(verbosity=0)
            suite = runner.build_suite()
            ids = {test.id() for test in iter_test_cases(suite)}
            assert not runner.test_loader.errors, runner.test_loader.errors
            baseline_ids = set()
            for package in ('content', 'users'):
                loader = unittest.TestLoader()
                baseline_ids.update(test.id() for test in iter_test_cases(
                    loader.discover(package, top_level_dir='.')))
                assert not loader.errors, loader.errors
            assert baseline_ids and baseline_ids <= ids, baseline_ids - ids
            compatibility_ids = {test.id() for test in iter_test_cases(
                unittest.TestLoader().loadTestsFromName('backend.tests.test_discovery'))}
            assert {name for name in ids if name.startswith('backend.')} == compatibility_ids
            assert 'backend.models' not in sys.modules
            assert not attempts, attempts
            assert not any(name.split('.')[0] in {'sqlalchemy', 'alembic'} for name in sys.modules)
            print('Legacy discovery preserved; no target dependency import attempted')
        ''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_explicit_target_modules_fail_when_dependencies_are_missing(self):
        for name in ('backend.tests.test_unit', 'backend.tests.test_postgres',
                     'backend.tests.test_remediation', 'backend.models'):
            with self.subTest(module=name):
                if name == 'backend.models':
                    code = 'import importlib; importlib.import_module(' + repr(name) + ')'
                else:
                    code = 'import unittest; unittest.main(module=None, argv=["unittest", ' + repr(name) + '])'
                result = self.run_python(code)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("ModuleNotFoundError: No module named 'sqlalchemy'", result.stderr)


if __name__ == '__main__':
    unittest.main()
