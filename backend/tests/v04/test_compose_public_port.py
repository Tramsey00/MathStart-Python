import os
import unittest
from unittest.mock import patch

from scripts.container_dev import public_origin
from scripts.team_local import publication_gateway_port


class ComposePublicPortTests(unittest.TestCase):
    def test_standard_and_custom_origins(self):
        for env, port in [({}, 8131), ({'MATHSTART_DEV_PUBLIC_PORT': '8133'}, 8133)]:
            with self.subTest(port=port), patch.dict(os.environ, env, clear=True):
                origin = f'http://127.0.0.1:{port}'
                settings = {'MATHSTART_PUBLIC_ORIGIN': public_origin()}
                self.assertEqual(settings['MATHSTART_PUBLIC_ORIGIN'], origin)
                self.assertEqual(publication_gateway_port({'origin': origin}, settings, settings), port)

    def test_rejects_reserved_port(self):
        with patch.dict(os.environ, {'MATHSTART_DEV_PUBLIC_PORT': '8132'}):
            with self.assertRaisesRegex(RuntimeError, 'Invalid Compose public port'):
                public_origin()

    def test_rejects_origin_mismatch_and_non_loopback(self):
        original = {'MATHSTART_PUBLIC_ORIGIN': 'http://127.0.0.1:8131'}
        custom = {'MATHSTART_PUBLIC_ORIGIN': 'http://127.0.0.1:8133'}
        with self.assertRaisesRegex(RuntimeError, 'origin must match'):
            publication_gateway_port({'origin': custom['MATHSTART_PUBLIC_ORIGIN']}, custom, original)
        external = {'MATHSTART_PUBLIC_ORIGIN': 'http://0.0.0.0:8133'}
        with self.assertRaisesRegex(RuntimeError, 'explicit loopback'):
            publication_gateway_port({'origin': external['MATHSTART_PUBLIC_ORIGIN']}, external, external)
