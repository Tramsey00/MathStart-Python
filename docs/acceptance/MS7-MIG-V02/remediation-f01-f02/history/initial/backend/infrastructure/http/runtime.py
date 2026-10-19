"""Explicit shadow-read startup. Identity/CSRF/HTML adapters await owner handoffs."""
import json
import os

from backend.infrastructure.database import DatabaseConfig, create_engine, check_connection
from backend.infrastructure.http.app import create_app
from backend.infrastructure.http.signing import Signer
from backend.content.releases import ReleaseStore


def application():
    key = os.environ.get('MATHSTART_HTTP_SIGNING_KEY')
    origin = os.environ.get('MATHSTART_PUBLIC_ORIGIN')
    if not key or not origin:
        raise ValueError('Explicit signing key and trusted public origin required')
    fallback = json.loads(os.environ.get('MATHSTART_HTTP_SIGNING_FALLBACK_KEYS', '[]'))
    if not isinstance(fallback, list) or any(not isinstance(k, str) or not k for k in fallback):
        raise ValueError('Invalid signing verifier key ring')
    engine = create_engine(DatabaseConfig.from_environment())
    check_connection(engine)
    root = os.environ.get('MATHSTART_RELEASE_ROOT')
    return create_app(engine, Signer(key, fallback), release_store=ReleaseStore(root) if root else None,
                      public_origin=origin)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(application(), host='127.0.0.1', port=8202, access_log=False)
