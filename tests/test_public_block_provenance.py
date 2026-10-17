"""A long public browser run must not bless a changed checkout as its input SHA."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.verify_public_block import assert_source_unchanged, source_snapshot


class PublicSourceGuard(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init','-q')
        self.git('config','user.name','Synthetic verification')
        self.git('config','user.email','synthetic@example.invalid')
        (self.root / '.gitignore').write_text('var/\n.cache/\n',encoding='utf-8')
        (self.root / 'source.py').write_text('version=1\n',encoding='utf-8')
        self.git('add','--','.gitignore','source.py')
        self.git('commit','-qm','Initial synthetic source')

    def git(self,*arguments):
        return subprocess.check_output(['git',*arguments],cwd=self.root,stderr=subprocess.STDOUT)

    def test_tracked_mutation_and_new_commit_each_fail_source_guard(self):
        before = source_snapshot(self.root)
        (self.root / 'source.py').write_text('version=2\n',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'source changed'):
            assert_source_unchanged(before,self.root)
        self.git('add','--','source.py')
        self.git('commit','-qm','Different synthetic source')
        with self.assertRaisesRegex(RuntimeError,'source changed'):
            assert_source_unchanged(before,self.root)

    def test_dirty_content_changes_are_detected_even_when_paths_stay_the_same(self):
        path = self.root / 'source.py'
        path.write_text('dirty=1\n',encoding='utf-8')
        before = source_snapshot(self.root)
        path.write_text('dirty=2\n',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'source changed'):
            assert_source_unchanged(before,self.root)

    def test_untracked_content_changes_are_detected(self):
        path = self.root / 'new.py'
        path.write_text('first\n',encoding='utf-8')
        before = source_snapshot(self.root)
        path.write_text('second\n',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'source changed'):
            assert_source_unchanged(before,self.root)

    def test_generated_runtime_and_cache_files_do_not_change_candidate(self):
        before = source_snapshot(self.root)
        for directory in ['var','.cache']:
            (self.root / directory).mkdir()
            (self.root / directory / 'generated').write_text('synthetic output\n')
        self.assertEqual(assert_source_unchanged(before,self.root),before)


if __name__ == '__main__':
    unittest.main()
