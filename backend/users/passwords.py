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


def supported_encoding(encoded):
    """Read-only cutover shape/support check; never asserts password validity."""
    if not isinstance(encoded, str) or not encoded:
        return False
    if encoded.startswith('!'):
        return True  # Retain deliberately unusable accounts without a reset.
    try:
        algorithm = encoded.split('$', 1)[0]
        if algorithm in {'pbkdf2_sha256', 'pbkdf2_sha1'}:
            _, count, salt, value = encoded.split('$')
            raw = base64.b64decode(value, validate=True)
            return (bool(re.fullmatch('[1-9][0-9]*', count)) and 0 < int(count) < 2**31 and bool(salt)
                    and len(raw) == (32 if algorithm == 'pbkdf2_sha256' else 20)
                    and base64.b64encode(raw).decode() == value)
        if algorithm == 'scrypt':
            _, n, salt, r, p, value = encoded.split('$')
            if not all(re.fullmatch('[1-9][0-9]*', item) for item in (n, r, p)):
                return False
            n, r, p = int(n), int(r), int(p)
            raw = base64.b64decode(value, validate=True)
            return (n > 1 and n & (n - 1) == 0 and r > 0 and p > 0 and bool(salt)
                    and n * r * 128 < 2**31 - 1 and len(raw) == 64
                    and base64.b64encode(raw).decode() == value)
        if algorithm == 'bcrypt_sha256':
            return re.fullmatch(r'bcrypt_sha256\$\$2[aby]\$(?:0[4-9]|[12][0-9]|3[01])\$[./A-Za-z0-9]{53}', encoded) is not None
        if algorithm == 'argon2':
            from argon2 import extract_parameters
            if not re.fullmatch(r'argon2\$argon2(?:id|i|d)\$(?:v=(?:16|19)\$)?m=[1-9][0-9]*,t=[1-9][0-9]*,p=[1-9][0-9]*\$[A-Za-z0-9+/]+\$[A-Za-z0-9+/]+', encoded):
                return False
            parameters = extract_parameters(encoded.removeprefix('argon2'))
            parts = encoded.split('$')
            for value in parts[-2:]:
                raw = base64.b64decode(value + '=' * (-len(value) % 4), validate=True)
                if base64.b64encode(raw).decode().rstrip('=') != value:
                    return False
            return (parameters.time_cost > 0 and parameters.parallelism > 0
                    and parameters.memory_cost >= 8 * parameters.parallelism
                    and parameters.salt_len >= 8 and parameters.hash_len >= 4
                    and all(re.fullmatch('[A-Za-z0-9+/]+', value) for value in parts[-2:]))
    except (ValueError, TypeError, OverflowError):
        return False
    return False


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
