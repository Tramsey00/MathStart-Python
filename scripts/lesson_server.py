"""Serve all published pages through one configured FastAPI origin; no startup seeding."""
import argparse
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', type=Path, default=ROOT / 'var/local/lesson-preview/private-env.json')
    args = parser.parse_args()
    values = json.loads(args.env_file.read_text(encoding='utf-8'))
    if not isinstance(values, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in values.items()):
        parser.error('Expected private string environment mapping')
    origin = urlsplit(values.get('MATHSTART_PUBLIC_ORIGIN', ''))
    if origin.scheme != 'http' or origin.hostname != '127.0.0.1' or not origin.port:
        parser.error('Explicit loopback HTTP origin and port required')
    os.environ.update(values)
    os.chdir(ROOT)
    import uvicorn
    from backend.content.public_runtime import application
    uvicorn.run(application(), host='127.0.0.1', port=origin.port, access_log=False, proxy_headers=False)


if __name__ == '__main__':
    main()
