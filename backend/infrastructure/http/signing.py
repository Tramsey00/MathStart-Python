"""Independent Django TimestampSigner/JSONSerializer compatibility implementation."""
import base64
import hashlib
import hmac
import json
import time
import zlib

from .transport import decode_json, invalid

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def base62(number):
    sign = "-" if number < 0 else ""
    number = abs(number)
    result = ""
    while number:
        number, remainder = divmod(number, 62)
        result = ALPHABET[remainder] + result
    return sign + (result or "0")


def b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


class Signer:
    def __init__(self, key, fallback_keys=(), clock=time.time):
        if not isinstance(key, str) or not key:
            raise ValueError("Explicit signing key required")
        self.key, self.fallback_keys, self.clock = key, tuple(fallback_keys), clock

    def signature(self, value, salt, key):
        derived = hashlib.sha256((salt + "signer" + key).encode()).digest()
        return b64(hmac.new(derived, value.encode(), hashlib.sha256).digest())

    def dumps(self, value, salt, *, compress=False):
        raw = json.dumps(value, separators=(",", ":"), allow_nan=False).encode("latin-1")
        compressed = zlib.compress(raw)
        use_compression = compress and len(compressed) < len(raw) - 1
        encoded = ("." if use_compression else "") + b64(compressed if use_compression else raw)
        signed = encoded + ":" + base62(int(self.clock()))
        return signed + ":" + self.signature(signed, salt, self.key)

    def loads(self, token, salt, *, max_length=1024):
        try:
            if not isinstance(token, str) or not token or len(token) > max_length:
                raise ValueError()
            signed, signature = token.rsplit(":", 1)
            if not any(hmac.compare_digest(signature, self.signature(signed, salt, key))
                       for key in (self.key, *self.fallback_keys)):
                raise ValueError()
            encoded, timestamp = signed.rsplit(":", 1)
            # Baseline has no max_age. Validate timestamp syntax without expiring it.
            if not timestamp.lstrip("-") or any(c not in ALPHABET for c in timestamp.lstrip("-")):
                raise ValueError()
            compressed = encoded.startswith(".")
            payload = encoded[1:] if compressed else encoded
            raw = base64.b64decode(payload + "=" * (-len(payload) % 4), altchars=b"-_", validate=True)
            if compressed:
                decoder = zlib.decompressobj()
                raw = decoder.decompress(raw, 65537)
                if len(raw) > 65536 or not decoder.eof or decoder.unused_data:
                    raise ValueError()
            if len(raw) > 65536:
                raise ValueError()
            return decode_json(raw)
        except (ValueError, TypeError, UnicodeError, RecursionError, zlib.error, OverflowError):
            raise invalid() from None
