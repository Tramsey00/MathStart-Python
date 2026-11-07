"""Post-Django boundary: real current data, explicit provenance and fail closed."""
import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts import legacy_oracle
from scripts.check_migration_preservation import ROOT, verify, dispositions, historical_artifact, workflow_changes
from scripts.verify_repo import parse_args, select_checks


class PlatformBoundaryTests(unittest.TestCase):
    def test_target_is_default_without_preparing_oracle(self):
        with patch.object(legacy_oracle, 'oracle_root', side_effect=AssertionError('Implicit oracle')):
            self.assertEqual(parse_args([]).profile, 'target')
            checks = select_checks(parse_args([]))
        self.assertEqual(len(checks), 15)
        self.assertFalse(any('manage.py' in part for row in checks for part in row.command))
        self.assertIsNone(importlib.util.find_spec('django'))
        self.assertIsNone(importlib.util.find_spec('rest_framework'))

    def test_target_runtime_and_shared_code_import_no_legacy_apps(self):
        files = [p for p in (ROOT / 'backend').rglob('*.py') if 'tests' not in p.parts]
        files += [ROOT / 'frontend' / name for name in ('rendering.py', 'build_public.py', 'ui_foundation.py')]
        for path in files:
            tree = ast.parse(path.read_bytes())
            for node in ast.walk(tree):
                names = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module or ''] if isinstance(node, ast.ImportFrom) else []
                self.assertFalse(any(name.split('.')[0] in {'django', 'rest_framework', 'content', 'users', 'config'} for name in names), str(path))

    def test_root_dependency_closure_does_not_install_django(self):
        visited = set()
        def packages(path):
            self.assertNotIn(path, visited)
            visited.add(path)
            result = []
            for line in path.read_text().splitlines():
                if line.startswith('-r '):
                    result += packages((path.parent / line[3:]).resolve())
                elif line and not line.startswith('#'):
                    result.append(line.split('==')[0].lower())
            return result
        self.assertFalse({'django', 'djangorestframework'} & set(packages(ROOT / 'requirements.lock')))

    def test_legacy_interpreter_has_no_combined_environment_fallback(self):
        with patch.dict('os.environ', {}, clear=True), self.assertRaises(RuntimeError):
            legacy_oracle.legacy_python()
        with patch.dict('os.environ', {'MATHSTART_LEGACY_PYTHON': sys.executable}), self.assertRaises(RuntimeError):
            legacy_oracle.legacy_python()

    def test_oracle_checkout_rejects_wrong_sha_and_dirty_tree(self):
        for results in ([legacy_oracle.DEFAULT_CHECKOUT.as_posix(), '0'*40],
                        [legacy_oracle.DEFAULT_CHECKOUT.as_posix(), legacy_oracle.ORACLE_SHA, ' M config/settings.py']):
            with patch.object(Path, 'exists', return_value=True), patch.object(legacy_oracle, 'git', side_effect=results), self.assertRaises(RuntimeError):
                legacy_oracle.oracle_root()

    def test_current_content_corruption_and_unknown_deletion_fail(self):
        original = Path.read_bytes
        content = ROOT / 'curriculum' / '5-klass'
        selected = next(content.rglob('body.html'))
        for missing in (False, True):
            def read(path):
                if path == selected:
                    if missing:
                        raise FileNotFoundError(str(path))
                    return b'unreviewed content edit'
                return original(path)
            with patch.object(Path, 'read_bytes', read), self.assertRaises((ValueError, FileNotFoundError)):
                verify()

    def test_removed_source_is_absent_and_shared_extraction_exact(self):
        rows = dispositions()
        for name, row in rows.items():
            if row['action'] in {'removed', 'moved'}:
                self.assertFalse((ROOT / name).exists(), name)
            if row['action'] == 'moved':
                followup = workflow_changes().get(row['destination'])
                if followup:
                    import hashlib
                    self.assertEqual(followup['before_sha256'], hashlib.sha256(historical_artifact(name)).hexdigest())
                    if followup['action'] == 'removed':
                        self.assertFalse((ROOT / row['destination']).exists())
                    else:
                        self.assertEqual(followup['after_sha256'], hashlib.sha256((ROOT / row['destination']).read_bytes()).hexdigest())
                else:
                    self.assertEqual((ROOT / row['destination']).read_bytes(), historical_artifact(name))
        for name in ('manage.py', 'config/settings.py', 'templates/base.html'):
            self.assertIn(name, rows)

    def test_old_approvals_are_not_recomputed_against_current_ci(self):
        manifest = json.loads((ROOT / 'specs/api/candidate-manifest-v1.json').read_bytes())
        import hashlib
        self.assertEqual(hashlib.sha256(historical_artifact('.github/workflows/ci.yml')).hexdigest(),
                         manifest['artifacts']['.github/workflows/ci.yml'])
        self.assertNotEqual((ROOT / '.github/workflows/ci.yml').read_bytes(), historical_artifact('.github/workflows/ci.yml'))


if __name__ == '__main__':
    unittest.main()
