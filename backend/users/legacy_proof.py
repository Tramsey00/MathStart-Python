"""Read-only verification of a legacy session for a future cutover import.

This is not target authentication. A caller must separately establish exclusive
writer/checkpoint provenance and a fresh same-owner password login before using
the resulting transfer binding. No bridge/session/receipt is created here.
"""
from dataclasses import dataclass
from datetime import datetime
import hmac
import re

from backend.infrastructure.http.signing import Signer
from backend.infrastructure.http.transport import APIError
from backend.users.security import salted_hmac, auth_hash


@dataclass(frozen=True)
class LegacyRegistrationProof:
    owner_user_id: int
    original_scope: str
    bootstrap_fingerprint: str
    transfer_binding_digest: str


def transfer_digest(session_key, user, key):
    # Binding changes if the password hash changes. A valid legacy session
    # signature alone never authorizes a new target session or receipt replay.
    return salted_hmac('mathstart.identity.cutover.transfer',
                       session_key + '\0' + str(user.id) + '\0' + auth_hash(user, key), key)


def session_owner(legacy_session, keys):
    """Verified routing hint only; full registration_proof is still required."""
    try:
        data = Signer(keys[0], keys[1:]).loads(legacy_session.session_data,
                    'django.contrib.sessions.SessionStore', max_length=131072)
    except APIError:
        return None
    owner = data.get('_auth_user_id') if isinstance(data, dict) else None
    if not isinstance(owner, str) or not re.fullmatch('[1-9][0-9]{0,9}', owner):
        return None
    return int(owner) if int(owner) < 2**31 else None


def registration_proof(legacy_session, user, keys, now):
    """Return a private verified fact or None, without DB/filesystem effects."""
    keys = tuple(keys)
    if not keys or any(not isinstance(key, str) or not key for key in keys):
        raise ValueError('Explicit retained verifier key ring required')
    if (type(user.id) is not int or not 0 < user.id < 2**31 or user.is_active is not True
            or not isinstance(user.password, str) or not isinstance(now, datetime) or now.tzinfo is None):
        return None
    session_key, expires = legacy_session.session_key, legacy_session.expire_date
    if (not isinstance(session_key, str) or not re.fullmatch('[A-Za-z0-9_-]{8,40}', session_key)
            or not isinstance(expires, datetime) or expires.tzinfo is None or expires <= now):
        return None
    try:
        # Django SessionBase.encode uses this exact TimestampSigner salt and
        # optional compressed JSON; expiry is the independently checked DB fact.
        data = Signer(keys[0], keys[1:]).loads(legacy_session.session_data,
                    'django.contrib.sessions.SessionStore', max_length=131072)
    except APIError:
        return None
    if not isinstance(data, dict):
        return None
    owner, backend, supplied_hash = (data.get(name) for name in
            ('_auth_user_id', '_auth_user_backend', '_auth_user_hash'))
    scope = data.get('identity_registration_scope')
    if (owner != str(user.id) or backend != 'django.contrib.auth.backends.ModelBackend'
            or not isinstance(supplied_hash, str) or not re.fullmatch('[a-f0-9]{64}', supplied_hash)
            or not any(hmac.compare_digest(supplied_hash, auth_hash(user, key)) for key in keys)
            or not isinstance(scope, str) or not re.fullmatch('bootstrap:[a-f0-9]{64}', scope)):
        return None
    return LegacyRegistrationProof(user.id, scope, scope.removeprefix('bootstrap:'),
                                   transfer_digest(session_key, user, keys[0]))
