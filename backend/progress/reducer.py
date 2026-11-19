"""Pinned R03 numerical rules + R03A status composition, with durable numeric cache."""
import hashlib
import json
from . import _r03_v1 as r03, _r03a_v1 as r03a


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def event_digest(events):
    return hashlib.sha256(encoded(sorted(events, key=r03.event_order)).encode()).hexdigest()


class StoredNumerical(r03a.NumericalReplay):
    def __init__(self, events, user_id, skill_id, result):
        # Result is from the transactionally maintained Progress cache, never a client DTO.
        object.__setattr__(self, 'user_id', user_id)
        object.__setattr__(self, 'skill_id', skill_id)
        object.__setattr__(self, '_events_json', encoded(events))
        object.__setattr__(self, '_result_json', encoded(result))


def project(events, facts, authority, user_id, skill_code, numerical=None):
    numeric = numerical if numerical is not None else r03.replay(events, str(user_id), skill_code)
    result = r03a.replay_completion_facts(StoredNumerical(events, str(user_id), skill_code, numeric), facts,
        authority={'context_version': 'assessment-completion-v1', 'records': authority})
    return numeric, result
