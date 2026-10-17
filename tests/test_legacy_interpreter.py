"""Execute a real isolated venv; resolving its POSIX symlink must fail this test."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import venv

from scripts.verify_public_block import legacy_executable


class LegacyInterpreterExecution(unittest.TestCase):
    def test_invoked_interpreter_keeps_venv_and_its_installed_modules(self):
        with tempfile.TemporaryDirectory() as directory:
            environment = Path(directory) / 'legacy environment'
            venv.EnvBuilder(with_pip=False, symlinks=os.name == 'posix').create(environment)
            executable = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            child_env = dict(os.environ)
            child_env.pop('PYTHONPATH', None)
            probe = 'import json,sys,sysconfig;print(json.dumps([sys.prefix,sys.base_prefix,sysconfig.get_path("purelib")]))'
            expected = json.loads(subprocess.check_output([str(executable), '-I', '-c', probe], env=child_env))
            module = Path(expected[2]) / 'legacy_environment_marker.py'
            module.write_text('VALUE = "installed-only-in-legacy-venv"\n', encoding='utf-8')
            command = [legacy_executable(executable), '-I', '-c',
                       'import json,sys,legacy_environment_marker as m;print(json.dumps([sys.prefix,sys.base_prefix,m.VALUE]))']
            actual = subprocess.run(command, capture_output=True, text=True, env=child_env)
            self.assertEqual(actual.returncode, 0, actual.stderr)
            identity = json.loads(actual.stdout)
            self.assertEqual(Path(identity[0]), environment)
            self.assertNotEqual(identity[0], identity[1])
            self.assertEqual(identity[2], 'installed-only-in-legacy-venv')
            if os.name == 'posix':
                self.assertTrue(executable.is_symlink(), 'This regression must exercise a real POSIX venv symlink')
                old = subprocess.run([str(executable.resolve()), '-I', '-c',
                                      'import legacy_environment_marker'], capture_output=True, text=True, env=child_env)
                self.assertNotEqual(old.returncode, 0, 'Negative control must escape the legacy venv')


if __name__ == '__main__':
    unittest.main()
