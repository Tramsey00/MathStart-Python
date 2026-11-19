"""Immutable read boundary. No Assessment ORM or public ingestion payload."""
from dataclasses import dataclass
import json
from uuid import UUID
from ._r03_v1 import ContractError


@dataclass(frozen=True)
class CompletedAttempt:
    attempt_id: str
    user_id: int
    version_id: str
    mode: str
    state: str
    completed_at: str
    # Tuple (stable skill code, outcome, independent_correct) from frozen Assessment authority.
    skills: tuple[tuple[str, str, bool], ...]
    evidence: 'Delivery'

    def validate(self):
        if (self.state != 'COMPLETED' or self.mode not in ('FINAL_ANSWER', 'STEP_BY_STEP', 'STRUCTURED_SOLUTION')
                or type(self.user_id) is not int or self.user_id <= 0 or type(self.skills) is not tuple
                or not self.skills or any(type(s) is not tuple or len(s) != 3 or type(s[2]) is not bool
                       or s[1] not in ('CORRECT','WRONG','UNSUPPORTED','INDETERMINATE') for s in self.skills)
                or len({s[0] for s in self.skills}) != len(self.skills)
                or not isinstance(self.evidence, Delivery)):
            raise ContractError('Verified assessed completion required')
        try:
            if any(str(UUID(value)) != value for value in (self.attempt_id, self.version_id)):
                raise ValueError()
        except (ValueError, TypeError, AttributeError):
            raise ContractError('Canonical native source UUID required') from None


@dataclass(frozen=True, init=False)
class Delivery:
    """Detached canonical JSON; returning .events/.facts never exposes mutable storage."""
    _json: str

    def __init__(self, *, events=(), facts=()):
        def no_float(value):
            if isinstance(value, float):
                raise ContractError('Binary floats are forbidden in Progress')
            if isinstance(value, dict):
                for v in value.values(): no_float(v)
            if isinstance(value, (list, tuple)):
                for v in value: no_float(v)
        no_float((events, facts))
        object.__setattr__(self, '_json', json.dumps({'events': list(events), 'facts': list(facts)},
            sort_keys=True, ensure_ascii=False, allow_nan=False))

    @property
    def events(self): return json.loads(self._json)['events']

    @property
    def facts(self): return json.loads(self._json)['facts']
