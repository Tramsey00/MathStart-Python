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
