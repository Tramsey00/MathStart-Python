"""Django-independent verification of the five accepted legacy hash formats."""
import base64
from difflib import SequenceMatcher
from functools import lru_cache
import gzip
import hashlib
import hmac
from pathlib import Path
import re
import secrets
import string

ITERATIONS = 1_000_000


def encode(password, salt=None, iterations=ITERATIONS):
    salt = salt or ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(22))
    result = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations)
    return f'pbkdf2_sha256${iterations}${salt}$' + base64.b64encode(result).decode()


def verify(password, encoded):
    if not isinstance(password, str) or not isinstance(encoded, str) or encoded.startswith('!'):
        return False
    try:
        algorithm = encoded.split('$', 1)[0]
        if algorithm in {'pbkdf2_sha256', 'pbkdf2_sha1'}:
            _, count, salt, expected = encoded.split('$', 3)
            count = int(count)
            if count < 1:
                return False
            raw = hashlib.pbkdf2_hmac(algorithm.removeprefix('pbkdf2_'), password.encode(), salt.encode(), count)
            result = hmac.compare_digest(base64.b64encode(raw).decode(), expected)
            if not result and count < ITERATIONS:
                hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), ITERATIONS - count)
            return result
        if algorithm == 'argon2':
            from argon2 import PasswordHasher, exceptions
            try:
                return PasswordHasher().verify(encoded.removeprefix('argon2'), password)
            except exceptions.VerificationError:
                return False
        if algorithm == 'bcrypt_sha256':
            import bcrypt
            value = hashlib.sha256(password.encode()).hexdigest().encode()
            return bcrypt.checkpw(value, encoded.removeprefix('bcrypt_sha256$').encode())
        if algorithm == 'scrypt':
            _, n, salt, r, p, expected = encoded.split('$', 5)
            raw = hashlib.scrypt(password.encode(), salt=salt.encode(), n=int(n), r=int(r), p=int(p),
                                 maxmem=2**31-1, dklen=64)
            return hmac.compare_digest(base64.b64encode(raw).decode(), expected)
    except (ValueError, TypeError, OverflowError):
        return False
    return False


@lru_cache(maxsize=1)
def common_passwords():
    return frozenset(gzip.decompress(Path(__file__).with_name('common-passwords.txt.gz').read_bytes()).decode().splitlines())


def validate_password(password, user):
    if len(password) < 8 or password.isdigit() or password.lower().strip() in common_passwords():
        return False
    candidate = password.lower()
    for name in ['username', 'first_name', 'last_name', 'email']:
        value = getattr(user, name, '') or ''
        for part in re.split(r'\W+', value.lower()) + [value.lower()]:
            # Same optimization and quick_ratio threshold as the accepted validator.
            if len(candidate) >= 10 * len(part) and len(part) < 0.7 / 2 * len(candidate):
                continue
            if SequenceMatcher(a=candidate, b=part).quick_ratio() >= 0.7:
                return False
    return True


def valid_username(value):
    return isinstance(value, str) and 1 <= len(value) <= 150 and re.fullmatch(r'[\w.@+-]+', value) is not None


def valid_email(value):
    # Registration's schema already provides the email format check; permit blank.
    if not value:
        return True
    from email.headerregistry import Address
    try:
        address = Address(addr_spec=value)
        return bool(address.username and address.domain and len(value) <= 254
                    and ('.' in address.domain or address.domain.lower() == 'localhost'))
    except (ValueError, IndexError):
        return False
