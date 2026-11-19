"""Explicit immutable policy mapping, also available in the API-only image."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from ._r03_v1 import ContractError


@lru_cache(maxsize=1)
def verify_policies():
    root = Path(__file__).resolve().parents[2]
    policy = json.loads((root/'specs/progress/policy-versions-v1.json').read_text(encoding='utf-8'))
    if (policy['numeric_policy'], policy['completion_policy'], policy['projection_policy']) != ('progress-v1','progress-v1.1','progress-v1.1'):
        raise ContractError('Unregistered Progress policy')
    for path in ('backend/progress/_r03_v1.py','backend/progress/_r03a_v1.py'):
        if sha256((root/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest() != policy['sources'][path]:
            raise ContractError('Progress policy source changed without version/review')
