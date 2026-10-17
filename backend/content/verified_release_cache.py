"""Bounded parsed-release reuse with full byte integrity checks on every load."""
from collections import OrderedDict
from copy import deepcopy
from hashlib import sha256
from threading import RLock
import re

from backend.content.releases import ReleaseStore, inside, _inside_resolved
from backend.infrastructure.http.transport import unavailable


class VerifiedReleaseStore(ReleaseStore):
    """Retain at most two validated editions; never cache publication authority.

    The accepted loader validates schemas and cross-file semantics on a miss.
    Every hit reads and hashes all validated bytes again, including the index,
    all page DTOs and all assets. Cached objects are private copies. DB gate,
    retention and descriptor validation remain in active_release at each call.
    """
    def __init__(self, root):
        super().__init__(root)
        self._editions = OrderedDict()
        self._lock = RLock()

    @staticmethod
    def _fingerprints(release):
        files = {'index.json': release.index_raw}
        files.update({f'pages/{pk}.json': raw for pk, raw in release.page_raw.items()})
        for metadata, raw in release.assets.values():
            path = metadata['storage_key']
            if path in files and files[path] != raw:
                raise unavailable()
            files[path] = raw
        return {path: (len(raw), sha256(raw).digest()) for path, raw in files.items()}

    def load(self, descriptor):
        if (not isinstance(descriptor.release_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', descriptor.release_id)
                or not isinstance(descriptor.manifest_digest, str)
                or not re.fullmatch(r'[a-f0-9]{64}', descriptor.manifest_digest)
                or type(descriptor.fence_generation) is not int or descriptor.fence_generation <= 0):
            raise unavailable()
        key = (descriptor.operation_id, descriptor.release_id, descriptor.manifest_digest, descriptor.fence_generation)
        with self._lock:
            cached = self._editions.get(key)
            if cached is None:
                release = super().load(descriptor)
                cached = (release, self._fingerprints(release))
                self._editions[key] = cached
                if len(self._editions) > 2:
                    self._editions.popitem(last=False)
            else:
                root = inside(self.root, descriptor.release_id)
                try:
                    for relative, (size, digest) in cached[1].items():
                        raw = _inside_resolved(root, relative).read_bytes()
                        if len(raw) != size or sha256(raw).digest() != digest:
                            raise unavailable()
                except OSError:
                    raise unavailable() from None
                self._editions.move_to_end(key)
            return deepcopy(cached[0])
