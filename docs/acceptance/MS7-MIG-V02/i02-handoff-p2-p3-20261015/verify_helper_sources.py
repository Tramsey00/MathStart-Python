"""Read-only byte integrity verifier for current helper-source evidence; no approval."""
import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path
import sys


def sha(raw):
    return sha256(raw).hexdigest()


def verify(bundle, pins, root):
    if bundle.get('version') != 'i02-helper-source-bytes-v2' or set(bundle['sources']) != set(pins):
        raise ValueError('SOURCE_SET')
    root = Path(root).resolve()
    for name, record in bundle['sources'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not name.startswith('var/'):
            raise ValueError('SOURCE_PATH')
        if record['source_encoding'] != 'utf-8':
            raise ValueError('SOURCE_ENCODING')
        raw = base64.b64decode(record['raw_bytes_base64'], validate=True)
        if sha(raw) != record['raw_sha256'] or sha(raw) != pins[name] or len(raw) != record['raw_size']:
            raise ValueError('RAW_SOURCE_DIGEST')
        text_raw = record['source_utf8'].encode('utf-8', errors='strict')
        if sha(text_raw) != record['source_utf8_sha256'] or text_raw != raw:
            raise ValueError('SOURCE_UTF8_ROUNDTRIP')
        if raw.decode('utf-8', errors='strict') != record['source_utf8']:
            raise ValueError('SOURCE_UTF8_DECODE')
        profile = {'bom_utf8': raw.startswith(b'\xef\xbb\xbf'), 'crlf': raw.count(b'\r\n'),
                   'cr': raw.count(b'\r'), 'lf': raw.count(b'\n')}
        if profile != record['byte_profile']:
            raise ValueError('SOURCE_BYTE_PROFILE')
        # Two physical reads are independent of the serialized text/base64 path.
        first, second = path.read_bytes(), path.read_bytes()
        if first != raw or second != raw or sha(first) != pins[name] or sha(second) != pins[name]:
            raise ValueError('PHYSICAL_SOURCE_BYTES')
    return {'sources': len(pins), 'physical_reads': 2 * len(pins), 'raw_and_utf8_roundtrip': 'PASS'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    try:
        bundle = json.loads((here / 'helper-sources-v2.json').read_bytes().decode('utf-8'))
        intake = json.loads((here / 'intake.json').read_bytes().decode('utf-8'))
        print(json.dumps(verify(bundle, intake['helper_source_pins'], args.root)))
        return 0
    except (ValueError, KeyError, OSError, UnicodeError) as error:
        print(json.dumps({'result': 'FAIL', 'error': str(error)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
