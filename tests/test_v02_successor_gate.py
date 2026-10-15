"""Synthetic guard regressions; these never approve or test a V02 successor."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('v02_successor_guard',ROOT/'scripts/v02_successor_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class SuccessorGuardTests(unittest.TestCase):
    def setUp(self):
        self.blob = dict(oid='a'*40,mode='100644',size=5,sha256='a'*64)
        self.row = dict(path='backend/content/releases.py',before=self.blob,
                        after=dict(self.blob,oid='b'*40,sha256='b'*64),attributes_sha256='c'*64)
        self.scope = dict(format='r03-v02-successor-reviewed-v1',status='REVIEWED_BY_R03',pr_number=53,
            predecessor_sha=gate.PREDECESSOR,predecessor_tree=gate.PREDECESSOR_TREE,base_sha=gate.BASE,
            control_revision=gate.CONTROL,anchor_sha256=gate.ANCHOR,implementation_sha='b'*40,tree_sha='c'*40,
            patch_sha256='d'*64,changes=[self.row],renderer_contract=dict(path='docs/acceptance/MS7-MIG-R03/renderer.md',sha256='e'*64),
            owner_handoff=dict(path='docs/acceptance/MS7-MIG-R03/handoff-fixture.md',sha256='f'*64),
            v02_case_ids=['backend.tests.v02.Synthetic.test_'+str(n) for n in range(86)])
        self.new = dict(sha='b'*40,tree={'sha':'c'*40},parents=[{'sha':gate.PREDECESSOR}])
        self.old = dict(sha=gate.PREDECESSOR,tree={'sha':gate.PREDECESSOR_TREE},parents=[{'sha':gate.BASE}])

    def validate(self,scope):
        raw = json.dumps(scope).encode()
        return gate.reviewed_scope(raw,gate.sha(raw))

    def test_exact_direct_successor_chain_and_reviewed_diff_metadata(self):
        gate.chain(self.new,self.old,self.validate(self.scope))
        gate.same_delta({self.row['path']:self.row['before']},{self.row['path']:self.row['after']},[self.row])

    def test_old_single_base_parent_rule_is_not_applied_to_successor(self):
        with self.assertRaisesRegex(RuntimeError,'SUCCESSOR_SINGLE_PREDECESSOR_PARENT'):
            gate.chain(dict(self.new,parents=[{'sha':gate.BASE}]),self.old,self.scope)

    def test_extra_or_merge_commit_and_rebased_history_rejected(self):
        for parents in ([],[{'sha':'e'*40}],[{'sha':gate.PREDECESSOR},{'sha':gate.BASE}]):
            with self.subTest(parents=parents),self.assertRaisesRegex(RuntimeError,'SUCCESSOR_SINGLE_PREDECESSOR_PARENT'):
                gate.chain(dict(self.new,parents=parents),self.old,self.scope)
        with self.assertRaisesRegex(RuntimeError,'ORIGINAL_HISTORY_CHANGED'):
            gate.chain(self.new,dict(self.old,parents=[{'sha':'e'*40}]),self.scope)

    def test_automatic_new_tree_or_head_pin_not_accepted(self):
        for k in ('sha','tree'):
            bad = dict(self.new,**{k:'d'*40 if k=='sha' else {'sha':'d'*40}})
            with self.assertRaisesRegex(RuntimeError,'NEW_COMMIT_OR_TREE_PIN'):
                gate.chain(bad,self.old,self.scope)
        self.scope['tree_sha'] = None
        with self.assertRaisesRegex(RuntimeError,'EXACT_NEW_PINS_REQUIRED'):
            self.validate(self.scope)

    def test_candidate_recomputed_scope_pins_need_independent_digest(self):
        raw = json.dumps(dict(self.scope,patch_sha256='f'*64)).encode()
        with self.assertRaisesRegex(RuntimeError,'INDEPENDENT_SCOPE_DIGEST'):
            gate.reviewed_scope(raw,gate.sha(json.dumps(self.scope).encode()))

    def test_original_anchor_control_parent_tree_cannot_be_replaced(self):
        for key in ('anchor_sha256','control_revision','base_sha','predecessor_sha','predecessor_tree'):
            with self.subTest(key=key),self.assertRaisesRegex(RuntimeError,'HISTORICAL_PINS_IMMUTABLE'):
                self.validate(dict(self.scope,**{key:'d'*len(self.scope[key])}))

    def test_workflow_locks_frozen_and_attributes_are_outside_scope(self):
        for path in ('.gitattributes','backend/content/.gitattributes','backend/requirements.lock',
                     '.github/workflows/ci.yml','specs/migration/r02-v1/frozen.json',
                     'docs/acceptance/MS7-MIG-V02/publication-byte-audit/round3/verify_publication_v3.py',
                     'docs/acceptance/MS7-MIG-V02/remediation-f01-f02/history/initial/report.md','../outside.py'):
            with self.subTest(path=path),self.assertRaisesRegex(RuntimeError,'SCOPED_PATH'):
                self.validate(dict(self.scope,changes=[dict(self.row,path=path)]))

    def test_deleted_executable_symlink_and_bad_oid_metadata_rejected(self):
        for after in (None,dict(self.row['after'],mode='100755'),dict(self.row['after'],mode='120000'),
                      dict(self.row['after'],oid='short')):
            with self.subTest(after=after),self.assertRaisesRegex(RuntimeError,'REGULAR_EXACT_BLOB_REQUIRED'):
                self.validate(dict(self.scope,changes=[dict(self.row,after=after)]))

    def test_unreviewed_path_blob_or_mode_change_rejected(self):
        before = {self.row['path']:self.row['before']}
        after = {self.row['path']:self.row['after']}
        with self.assertRaisesRegex(RuntimeError,'EXACT_CHANGED_PATH_SET'):
            gate.same_delta(before,{**after,'extra.py':self.row['after']},[self.row])
        for key,value in [('mode','100755'),('sha256','f'*64),('size',6),('oid','f'*40)]:
            with self.subTest(key=key),self.assertRaisesRegex(RuntimeError,'REVIEWED_BLOB_METADATA'):
                gate.same_delta(before,{self.row['path']:dict(self.row['after'],**{key:value})},[self.row])

    def test_no_empty_duplicate_or_missing_case_inventory(self):
        for ids in ([],self.scope['v02_case_ids'][:-1],self.scope['v02_case_ids']+self.scope['v02_case_ids'][:1]):
            with self.subTest(count=len(ids)),self.assertRaisesRegex(RuntimeError,'EXACT_CASE_INVENTORY_REQUIRED'):
                self.validate(dict(self.scope,v02_case_ids=ids))

    def test_unknown_fields_and_duplicate_json_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'SCOPE_SCHEMA'):
            self.validate(dict(self.scope,allow_unreviewed=True))
        with self.assertRaisesRegex(RuntimeError,'DUPLICATE_KEY'):
            gate.decode(b'{"tree_sha":"a","tree_sha":"b"}')

    def test_pending_intake_stops_before_library_network_or_execution(self):
        with tempfile.TemporaryDirectory(prefix='r03-successor-',dir=ROOT.parent) as d:
            p = Path(d)/'pending.json';raw=b'{"status":"AWAITING_PUBLISHED_SUCCESSOR"}'
            p.write_bytes(raw)
            with patch.object(gate,'library') as load:
                with self.assertRaisesRegex(RuntimeError,'NOT_READY_REVIEWED_DIFF_AND_INPUTS_REQUIRED'):
                    gate.execute(p,gate.sha(raw),'b'*40,Path(d)/'unused',Path(d)/'evidence')
                load.assert_not_called()

    def test_unreviewed_renderer_handoff_cannot_come_from_candidate(self):
        for key in ('renderer_contract','owner_handoff'):
            with self.subTest(key=key),self.assertRaisesRegex(RuntimeError,'R03_REVIEWED_HANDOFF_REQUIRED'):
                self.validate(dict(self.scope,**{key:dict(path='backend/infrastructure/http/README.md',sha256='e'*64)}))

    def test_original_published_launcher_and_receipt_are_still_pinned(self):
        gate.library()
        raw = (ROOT/'docs/acceptance/MS7-MIG-R03/v02-review-20261015/38642117604-v02-tests.json').read_bytes()
        self.assertEqual(gate.sha(raw),gate.PREDECESSOR_CASES_SHA)


if __name__=='__main__':
    unittest.main()
