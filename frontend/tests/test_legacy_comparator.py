"""The live comparator must launch the historical venv, including POSIX links."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from frontend.legacy_comparator import legacy_executable


class LegacyInterpreterIdentity(unittest.TestCase):
    def test_lexical_venv_path_is_not_resolved_to_base_python(self):
        with tempfile.TemporaryDirectory() as directory:
            executable=Path(directory)/'legacy-venv'/'bin'/'python'
            with patch.object(Path,'resolve',side_effect=AssertionError('Venv identity must not be dereferenced')):
                self.assertEqual(legacy_executable(executable),str(executable.absolute()))

    def test_actual_posix_venv_symlink_keeps_its_invocation_path(self):
        # POSIX CI exercises a real symlink. Windows launchers are regular EXEs,
        # whose lexical-path contract is covered by the other platform-neutral test.
        if os.name!='posix':
            self.assertEqual(legacy_executable(sys.executable),str(Path(sys.executable).absolute()))
            return
        with tempfile.TemporaryDirectory() as directory:
            executable=Path(directory)/'legacy-venv'/'bin'/'python'
            executable.parent.mkdir(parents=True)
            executable.symlink_to(Path(sys.executable).resolve())
            self.assertNotEqual(executable,executable.resolve())
            self.assertEqual(legacy_executable(executable),str(executable.absolute()))
