"""Renderer failure isolation and build receipt trust-boundary tests."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from frontend.build_input import verified_release
from frontend.rendering import catalogue_html, PublicRenderer


class ArtifactBoundary(unittest.TestCase):
    def test_invalid_receipt_is_rejected_before_any_dto_interpretation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'release';root.mkdir();(root/'receipt.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'receipt digest mismatch'):
                verified_release(tmp,'release','a'*64,'b'*64)

    def test_missing_added_or_changed_receipt_files_fail_closed(self):
        for mutation in ('missing','added','changed'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)/'release';root.mkdir();raw=b'{}';(root/'index.json').write_bytes(raw)
                receipt=json.dumps({'version':'build-input-receipt-v1','release_id':'release','manifest_digest':'a'*64,'files':[{'path':'index.json','size':2,'sha256':sha256(raw).hexdigest()}]}).encode()
                (root/'receipt.json').write_bytes(receipt)
                if mutation=='missing':(root/'index.json').unlink()
                if mutation=='added':(root/'extra').write_bytes(b'extra')
                if mutation=='changed':(root/'index.json').write_bytes(b'[]')
                with self.assertRaises((ValueError,OSError)):
                    verified_release(tmp,'release','a'*64,sha256(receipt).hexdigest())

    def test_catalogue_escapes_query_and_labels_and_preserves_int64_ids(self):
        context={'catalogue_full':{'grades':[],'subjects':[],'sections':[]},'catalogue_query':'<script>&"',
            'catalogue_grades':[],'catalogue_subjects':[],'catalogue_grade':'','catalogue_subject':'',
            'catalogue_count':1,'catalogue_topics':[{'id':9223372036854775807,'title':'<unsafe>',
                'url':'/safe/','grade_id':None,'subject_id':None,'section_id':None}]}
        rendered=catalogue_html(context)
        self.assertNotIn('<unsafe>',rendered);self.assertNotIn('<script>',rendered)
        self.assertIn('&lt;unsafe&gt;',rendered);self.assertIn('/safe/',rendered)

    def test_renderer_refuses_unpinned_release_before_reading_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'Pinned release required'):
                PublicRenderer(tmp)({}, {}, 'http://localhost/')

if __name__=='__main__':unittest.main()
