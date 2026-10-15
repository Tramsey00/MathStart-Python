import json
from pathlib import Path
import tempfile
import unittest
import asyncio
from unittest.mock import patch

from django.conf import settings
from django.core import signing as old
from starlette.datastructures import QueryParams
from starlette.requests import Request

from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http.transport import APIError, singleton_query, page_size, decode_json
from backend.content.releases import safe_public_path
from backend.infrastructure.http.transport import parse_request
from backend.staff.publication import observe
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from backend.tests.v02.fixtures import KEY, STAMP, release_files

if not settings.configured:
    settings.configure(SECRET_KEY=KEY, SECRET_KEY_FALLBACKS=[])


class UnitContractTests(unittest.TestCase):
    def test_old_new_signer_exact_bytes_compressed_and_keyring(self):
        salt = 'content.grades.http-v1.cursor'
        payload = {'scope': 'public:/api/v1/grades/', 'page_size': 1, 'created_at': STAMP.isoformat(), 'id': 70}
        for compress in [False, True]:
            with patch('django.core.signing.time.time', return_value=1234567):
                previous = old.dumps(payload, key=KEY, salt=salt, compress=compress)
            signer = Signer(KEY, clock=lambda: 1234567)
            self.assertEqual(signer.dumps(payload, salt, compress=compress), previous)
            self.assertEqual(signer.loads(previous, salt), payload)
            self.assertEqual(old.loads(signer.dumps(payload, salt), key=KEY, salt=salt), payload)
            self.assertEqual(Signer('new-key', [KEY]).loads(previous, salt), payload)
        # No expiration is added: accepted legacy loads does not use max_age.
        self.assertEqual(Signer(KEY, clock=lambda: 9999999999).loads(previous, salt), payload)
        for token, scope in [(previous + 'x', salt), (previous, 'wrong-salt'), ('x' * 1025, salt)]:
            with self.assertRaises(APIError):
                signer.loads(token, scope)

    def test_raw_json_duplicate_nonfinite_utf8_and_query_negatives(self):
        for raw in [b'{"x":1,"x":2}', b'{"x":{"a":1,"a":2}}', b'{"x":NaN}', b'\xff', b'{']:
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeError)):
                decode_json(raw)
        for query in ['page_size=1&page_size=2', 'cursor=x&cursor=y', 'unknown=x']:
            with self.assertRaises(APIError):
                singleton_query(QueryParams(query), {'cursor', 'page_size'})
        for raw in ['0', '101', '1000', 'true', '1.1', '２０', '']:
            with self.assertRaises(APIError):
                page_size(raw)

    def test_complete_snapshot_catalogue_secrecy_and_unicode(self):
        with tempfile.TemporaryDirectory(dir='var') as root:
            store, descriptor, index, deliveries = release_files(root)
            release = store.load(descriptor)
            self.assertEqual(release.page_path('/glavnaya/')['seo']['canonical_path'], '/')
            self.assertEqual(release.catalogue(QueryParams('q=strasse&grade=unknown&extra=ignored'))['catalogue_count'], 1)
            self.assertEqual(release.catalogue(QueryParams('q=miss&q=Straße'))['catalogue_count'], 1)
            self.assertEqual(release.catalogue(QueryParams('subject=foreign'))['catalogue_subject'], '')
            self.assertNotIn('draft', json.dumps(release.index))
            self.assertEqual(set(release.assets), {'/static/theme.css'})

    def test_missing_asset_changed_payload_private_field_and_invalid_manifest(self):
        for mutate in ['asset', 'body', 'private', 'relation']:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory(dir='var') as root:
                store, descriptor, index, deliveries = release_files(root)
                base = Path(root) / descriptor.release_id
                if mutate == 'asset':
                    (base / 'assets/theme.css').write_bytes(b'changed')
                else:
                    data = deliveries[302]
                    if mutate == 'body': data['body_html'] = 'tampered'
                    if mutate == 'private': data['answer_key'] = 'secret'
                    if mutate == 'relation': data['grade_id'] = 999
                    (base / 'pages/302.json').write_text(json.dumps(data), encoding='utf-8')
                with self.assertRaises(APIError) as raised:
                    store.load(descriptor)
                self.assertEqual(raised.exception.status, 503)

    def test_redirect_and_path_traversal_safety(self):
        self.assertTrue(safe_public_path('/старое.html'))
        for path in ['//evil.test', '/a/../secret', '/a/%252e%252e/x', '/a\\b', '/admin/', '/api/v1/', '/x\n', '/x?y', 'file:///x']:
            self.assertFalse(safe_public_path(path), path)

    def test_raw_boundary_schema_content_type_and_stream_limit(self):
        async def parse(raw, content_type):
            sent = False
            async def receive():
                nonlocal sent
                if sent:
                    return {'type': 'http.disconnect'}
                sent = True
                return {'type': 'http.request', 'body': raw, 'more_body': False}
            request = Request({'type': 'http', 'headers': [(b'content-type', content_type.encode())]}, receive)
            return await parse_request(request, 'EmptyRequest')
        self.assertEqual(asyncio.run(parse(b'{}', 'application/json; charset="UTF-8"')), {})
        for raw, mime in [(b'{', 'application/json'), (b'{"extra":true}', 'application/json'),
                          (b'{}', 'text/plain'), (b'{}', 'application/json; charset=latin-1'),
                          (b'{"a":1,"a":2}', 'application/json'), (b'\xff', 'application/json')]:
            with self.subTest(mime=mime), self.assertRaises(APIError) as raised:
                asyncio.run(parse(raw, mime))
            self.assertEqual(raised.exception.status, 400)
        with self.assertRaises(APIError) as raised:
            asyncio.run(parse(b' ' * 65537, 'application/json'))
        self.assertEqual(raised.exception.code, 'LIMIT_EXCEEDED')

    def test_publication_observer_coherence_retry_and_no_fabricated_sync(self):
        edition = {'release_id': 'active', 'manifest_digest': 'a' * 64, 'page_published': True,
                   'page_digest': 'b' * 64, 'canonical_path': '/topic/'}
        data = {'page_id': 302, 'observed_at': STAMP.isoformat(), 'state': 'IN_SYNC',
                'active': edition, 'db_edition': deepcopy(edition), 'pending': None}
        sample = ({'release_id': 'active', 'manifest_digest': 'a' * 64}, {'pending_operation_id': None}, None, None)
        with patch('backend.staff.publication.authority_sample', return_value=sample):
            self.assertEqual(observe(object(), 302, 'public', lambda *_: data), data)
            changed = deepcopy(data); changed['db_edition']['release_id'] = 'foreign'
            with self.assertRaises(APIError):
                observe(object(), 302, 'public', lambda *_: changed)
        with patch('backend.staff.publication.authority_sample', side_effect=[sample, (None, None, None, None)] * 3) as sampler:
            with self.assertRaises(APIError):
                observe(object(), 302, 'public', lambda *_: data)
            self.assertEqual(sampler.call_count, 6)

    def test_request_id_propagates_within_request_and_client_role_is_untrusted(self):
        from backend.infrastructure.http.transport import success, error_response, invalid
        from backend.staff.authorization import authorize
        request = Request({'type': 'http', 'headers': []})
        ok = json.loads(success(request, []).body)
        bad = json.loads(error_response(request, invalid()).body)
        self.assertEqual(ok['meta']['request_id'], bad['error']['request_id'])
        with self.assertRaises(APIError) as raised:
            authorize(object(), {'user_id': 902, 'is_superuser': True})
        self.assertEqual(raised.exception.status, 401)

    def test_staff_search_tokenization_matches_native_quoted_and_unicode_cases(self):
        from backend.staff.reads import search_terms
        from django.utils.text import smart_split, unescape_string_literal
        for query in ['plain words', '"Private draft"', 'one"two three"', "one'two three'",
                      '"escaped \\" word"', "'unclosed phrase", 'Straße\u2003слово', "'"]:
            expected = [unescape_string_literal(word) if word[0] in {'"', "'"} and word[0] == word[-1] else word
                        for word in smart_split(query)]
            self.assertEqual(search_terms(query), expected, query)


class I02HandoffUnitTests(unittest.TestCase):
    def setUp(self):
        self.files = tempfile.TemporaryDirectory(dir='var')
        self.addCleanup(self.files.cleanup)
        self.store, self.descriptor, self.index, self.deliveries = release_files(self.files.name)

    def write_index(self):
        raw = json.dumps(self.index, ensure_ascii=False).encode('utf-8')
        (self.store.root / self.descriptor.release_id / 'index.json').write_bytes(raw)
        self.descriptor = replace(self.descriptor, manifest_digest=sha256(raw).hexdigest())
        return self.store.load(self.descriptor)

    def test_home_requires_slug_alias_even_with_valid_manifest_digest(self):
        self.index['aliases'] = []
        with self.assertRaises(APIError) as raised:
            self.write_index()
        self.assertEqual((raised.exception.status, raised.exception.code), (503, 'SERVICE_UNAVAILABLE'))
        raw = (self.store.root / self.descriptor.release_id / 'index.json').read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), self.descriptor.manifest_digest)

    def test_home_alias_invalid_reference_status_canonical_duplicate_and_extra(self):
        original = deepcopy(self.index['aliases'])
        variants = [[{**original[0], **change}] for change in (
            {'page_id': 999}, {'page_id': 302}, {'status': 301}, {'canonical_path': '/topic/'})]
        variants += [original * 2, original + [{**original[0], 'url': '/extra-home/'}]]
        for aliases in variants:
            with self.subTest(aliases=aliases), self.assertRaises(APIError) as raised:
                self.index['aliases'] = aliases
                self.write_index()
            self.assertEqual((raised.exception.status, raised.exception.code), (503, 'SERVICE_UNAVAILABLE'))

    def test_home_alias_uses_actual_slug_and_canonical_root(self):
        self.assertEqual(self.store.load(self.descriptor).page_path('/glavnaya/')['id'], 301)
        self.deliveries[301]['slug'] = 'welcome-home'
        (self.store.root / self.descriptor.release_id / 'pages/301.json').write_text(
            json.dumps(self.deliveries[301]), encoding='utf-8')
        self.index['pages'][0]['slug'] = 'welcome-home'
        self.index['aliases'][0]['url'] = '/welcome-home/'
        release = self.write_index()
        self.assertEqual(release.page_path('/')['id'], 301)
        self.assertEqual(release.page_path('/welcome-home/')['seo']['canonical_path'], '/')

    def test_catalogue_release_without_home_does_not_require_alias(self):
        self.index['pages'] = [p for p in self.index['pages'] if p['page_type'] != 'home']
        self.index['aliases'] = []
        release = self.write_index()
        self.assertEqual(release.page_path('/topic/')['id'], 302)
        with self.assertRaises(APIError) as raised:
            release.page_path('/')
        self.assertEqual(raised.exception.status, 404)
        context = release.renderer_context(release.page('karta-sajta'), QueryParams('q=strasse'))
        self.assertEqual(context['catalogue_full'], self.index['catalogue'])
        self.assertEqual(context['catalogue_count'], 1)

    def test_renderer_catalogue_full_preserves_structure_for_all_filters(self):
        release = self.store.load(self.descriptor)
        for query, count in [('', 1), ('q=strasse', 1), ('q=none', 0),
                             ('grade=unknown&subject=foreign&ignored=x', 1),
                             ('grade=5-klass&subject=matematika&q=none', 0),
                             ('q=miss&q=Stra%C3%9Fe', 1)]:
            with self.subTest(query=query):
                params = QueryParams(query)
                context = release.renderer_context(release.page('karta-sajta'), params)
                self.assertEqual(set(context), set(release.catalogue(params)) | {'catalogue_full', 'pinned_release'})
                self.assertEqual({k: context[k] for k in release.catalogue(params)}, release.catalogue(params))
                self.assertEqual(context['catalogue_count'], count)
                self.assertEqual(context['catalogue_full'], self.index['catalogue'])
                self.assertEqual(context['pinned_release'], {
                    'release_id': self.descriptor.release_id, 'manifest_digest': self.descriptor.manifest_digest})

    def test_renderer_context_deeply_isolates_filtered_and_full_catalogue(self):
        release = self.store.load(self.descriptor)
        original = deepcopy(release.index)
        context = release.renderer_context(release.page('karta-sajta'), QueryParams())
        context['catalogue_topics'][0]['title'] = 'renderer mutation'
        context['catalogue_grades'][0]['title'] = 'renderer grade mutation'
        context['catalogue_subjects'][0]['title'] = 'renderer subject mutation'
        context['catalogue_full']['sections'][0]['title'] = 'renderer section mutation'
        context['catalogue_full']['topics'].clear()
        context['pinned_release']['release_id'] = 'foreign'
        self.assertEqual(release.index, original)
        self.assertEqual(release.descriptor, self.descriptor)
        self.assertEqual(release.renderer_context(release.page('karta-sajta'), QueryParams())['catalogue_full'], original['catalogue'])

    def test_renderer_non_catalogue_pages_receive_only_release_identity(self):
        release = self.store.load(self.descriptor)
        for slug in ['glavnaya', 'topic']:
            self.assertEqual(release.renderer_context(release.page(slug), QueryParams('q=ignored')), {
                'pinned_release': {'release_id': self.descriptor.release_id,
                                   'manifest_digest': self.descriptor.manifest_digest}})

    def test_renderer_int64_ids_are_exact_python_integers(self):
        large_id = 2**53 + 1
        for row in self.index['catalogue']['grades']:
            row['id'] = large_id
        self.index['catalogue']['subjects'][0]['grade_id'] = large_id
        self.index['catalogue']['topics'][0]['grade_id'] = large_id
        self.deliveries[302]['grade_id'] = large_id
        (self.store.root / self.descriptor.release_id / 'pages/302.json').write_text(
            json.dumps(self.deliveries[302]), encoding='utf-8')
        release = self.write_index()
        context = release.renderer_context(release.page('karta-sajta'), QueryParams())
        for value in [context['catalogue_full']['grades'][0]['id'],
                      context['catalogue_full']['subjects'][0]['grade_id'],
                      context['catalogue_topics'][0]['grade_id']]:
            self.assertIs(type(value), int)
            self.assertEqual(value, large_id)


class HelperEvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        import base64
        import importlib.util
        self.root = Path(__file__).resolve().parents[3]
        self.evidence = self.root / 'docs/acceptance/MS7-MIG-V02/i02-handoff-p2-p3-20261015'
        spec = importlib.util.spec_from_file_location('i02_helper_integrity', self.evidence / 'verify_helper_sources.py')
        self.verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.verifier)
        self.bundle = json.loads((self.evidence / 'helper-sources-v2.json').read_bytes().decode('utf-8'))
        self.pins = json.loads((self.evidence / 'intake.json').read_bytes().decode('utf-8'))['helper_source_pins']
        # Reconstruct fixtures from retained bytes: a clean checkout need not
        # contain ignored local verification scripts. The separate CLI receipt
        # verifies the actual original files with two physical reads each.
        sources = tempfile.TemporaryDirectory(dir='var')
        self.addCleanup(sources.cleanup)
        self.source_root = Path(sources.name)
        for name, record in self.bundle['sources'].items():
            path = self.source_root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(base64.b64decode(record['raw_bytes_base64'], validate=True))

    def test_p3_sources_roundtrip_and_two_physical_reads_match_original_byte_pins(self):
        result = self.verifier.verify(self.bundle, self.pins, self.source_root)
        self.assertEqual(result, {'sources': 5, 'physical_reads': 10, 'raw_and_utf8_roundtrip': 'PASS'})

    def test_p3_corrupted_text_or_jointly_rehashed_source_fails(self):
        import base64
        name = 'var/i02_handoff_full_content.py'
        for joint in [False, True]:
            with self.subTest(joint=joint), self.assertRaises(ValueError):
                bundle = deepcopy(self.bundle)
                record = bundle['sources'][name]
                record['source_utf8'] += '\n# corrupted source\n'
                text_raw = record['source_utf8'].encode('utf-8')
                record['source_utf8_sha256'] = sha256(text_raw).hexdigest()
                if joint:
                    record.update(raw_bytes_base64=base64.b64encode(text_raw).decode('ascii'),
                                  raw_sha256=sha256(text_raw).hexdigest(), raw_size=len(text_raw))
                self.verifier.verify(bundle, self.pins, self.source_root)

    def test_p3_reported_hashes_are_cp1251_misreads_and_fail_explicit_utf8_guard(self):
        original = self.root / 'docs/acceptance/MS7-MIG-V02/i02-handoff-followup-20261015/raw-command-receipts.json'
        raw = original.read_bytes()
        correct, wrong = json.loads(raw.decode('utf-8')), json.loads(raw.decode('cp1251'))
        expected = {'var/i02_handoff_full_content.py': '3a10fc80fe13e3965931f11d2e168f4352bd96e89504cdf3f6cb60b9af8aa28d',
                    'var/i02_handoff_finalize.py': '0d45e3ef0ba0654f0e16e8e7e715fe7bfc66c1fc433c6fd26d639472d88b69d3'}
        for name, bad_hash in expected.items():
            with self.subTest(name=name):
                good = correct['reproduction_helper_sources'][name]['source_utf8']
                bad = wrong['reproduction_helper_sources'][name]['source_utf8']
                self.assertEqual(sha256(good.encode('utf-8')).hexdigest(), self.pins[name])
                self.assertEqual(sha256(bad.encode('utf-8')).hexdigest(), bad_hash)
                self.assertEqual(sha256(bad.encode('cp1251')).hexdigest(), self.pins[name])
                bundle = deepcopy(self.bundle)
                bundle['sources'][name]['source_utf8'] = bad
                bundle['sources'][name]['source_utf8_sha256'] = bad_hash
                with self.assertRaises(ValueError):
                    self.verifier.verify(bundle, self.pins, self.source_root)

    def test_p3_encoding_and_raw_byte_profile_tampering_fail(self):
        name = 'var/i02_handoff_finalize.py'
        for change in [{'source_encoding': 'cp1251'}, {'raw_bytes_base64': 'not base64!'},
                       {'byte_profile': {'bom_utf8': True, 'cr': 0, 'lf': 261, 'crlf': 0}}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                bundle = deepcopy(self.bundle)
                bundle['sources'][name].update(change)
                self.verifier.verify(bundle, self.pins, self.source_root)
        path = self.source_root / name
        path.write_bytes(path.read_bytes() + b'\n# physical source corruption\n')
        with self.assertRaisesRegex(ValueError, 'PHYSICAL_SOURCE_BYTES'):
            self.verifier.verify(self.bundle, self.pins, self.source_root)
