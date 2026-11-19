"""Only Progress writes its append-only evidence and rebuildable exact projection.

All methods taking a Session participate in the caller's transaction (N013 may
atomically finalize there). They never commit, perform math or call a provider.
"""
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from backend.knowledge.models import skill
from backend.models.baseline import utc_now
from . import _r03_v1 as r03, _r03a_v1 as r03a
from .contracts import CompletedAttempt, Delivery
from .models import attempt_binding, completion, event, state
from .reducer import encoded, event_digest, project

EVENT_FIELDS = frozenset(('event_id user_id skill_id event_kind policy_version occurred_at attempt_id evidence_ref '
    'difficulty completed_at misconception_code confirmed source_kind independent_evidence_rule hint_used reveal_used').split())


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None


def locks(session, identities):
    for identity in sorted(set(identities)):
        session.execute(sa.text('SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))'), {'key': 'progress:' + identity})


def canonical_event(raw):
    if set(raw) - EVENT_FIELDS:
        raise r03.ContractError('Unknown Progress event fields')
    value = r03.validate_event(raw)
    return value


class ProgressService:
    def __init__(self, *, read_completion=None, verify_binding=None):
        from .policies import verify_policies
        verify_policies()
        from backend.assessment.completion_read import read_completed_attempt, verify_version_skills
        self.read_completion = read_completion or read_completed_attempt
        self.verify_binding = verify_binding or verify_version_skills

    def skills(self, session, codes):
        rows = session.execute(sa.select(skill.c.id, skill.c.code).where(skill.c.code.in_(codes))).all()
        result = {row.code: row.id for row in rows}
        if result.keys() != set(codes) or not set(codes) <= r03.PILOT_CODES:
            raise r03.ContractError('Unknown skill')
        return result

    def _scope(self, session, user_id, skill_id, *, numerical_changed=False, force=False):
        code = session.scalar(sa.select(skill.c.code).where(skill.c.id == skill_id))
        events = list(session.scalars(sa.select(event.c.payload).where(event.c.user_id == user_id, event.c.skill_id == skill_id)))
        rows = session.execute(sa.select(completion.c.payload, completion.c.authority).where(
            completion.c.user_id == user_id, completion.c.skill_id == skill_id)).all()
        facts, authority = [], []
        for row in rows:
            # Revalidate retained source provenance, including explicit legacy contexts.
            r03a._authority_records(row.authority)
            facts.append(row.payload)
            record = dict(row.authority['records'][0])
            record['attempt_state'] = 'COMPLETED'  # verified mirror view, original provenance retained unchanged
            authority.append(record)
        old = session.execute(sa.select(state).where(state.c.user_id == user_id, state.c.skill_id == skill_id)).first()
        digest = event_digest(events)
        numeric = None
        if old and not numerical_changed and not force:
            if old.event_digest != digest:
                raise r03.ContractError('Projection cache disagrees with immutable log; explicit replay required')
            numeric = old.numerical
        numeric, result = project(events, facts, authority, user_id, code, numeric)
        values = result['state']
        stored = dict(user_id=user_id, skill_id=skill_id, mastery=Decimal(values['mastery']),
            confidence=Decimal(values['confidence']), evidence_count=values['evidence_count'], status=values['status'],
            last_updated=instant(values['last_updated']), reducer_version=values['reducer_version'],
            numerical=numeric, event_digest=digest, result=result)
        session.execute(insert(state).values(**stored).on_conflict_do_update(
            index_elements=[state.c.user_id, state.c.skill_id], set_={k: v for k, v in stored.items() if k not in ('user_id', 'skill_id')}))
        return result

    def ingest(self, session, delivery):
        with session.begin_nested():
            return self._ingest(session, delivery)

    def _ingest(self, session, delivery):
        if not isinstance(delivery, Delivery):
            raise r03.ContractError('Immutable Progress delivery required')
        events = [canonical_event(e) for e in delivery.events]
        facts = [r03a.validate_completion_fact(f) for f in delivery.facts]
        if any(e['event_kind'] == 'SELF_REPORTED_KNOWN' for e in events):
            raise r03.ContractError('Self-report uses its separate authenticated service')
        attempts = {v['attempt_id'] for v in events + facts}
        # Global identities are locked before scope filtering, including foreign owners.
        ids = ['0:attempt:' + a for a in attempts]
        ids += ['1:event:' + e['event_id'] for e in events]
        ids += ['2:completion:' + f['completion_id'] for f in facts]
        scopes = {(int(v['user_id']), v['skill_id']) for v in events + facts}
        ids += [f'3:scope:{u}:{s}' for u, s in scopes]
        locks(session, ids)
        sources = {}
        for attempt_id in sorted(attempts):
            source = self.read_completion(session, attempt_id)
            if not isinstance(source, CompletedAttempt):
                raise r03.ContractError('Trusted immutable Assessment projection required')
            source.validate()
            if source.attempt_id != attempt_id:
                raise r03.ContractError('Assessment source identity mismatch')
            self.verify_binding(session, source)
            sources[attempt_id] = source
        for value in events + facts:
            source = sources[value['attempt_id']]
            if value['user_id'] != str(source.user_id):
                raise r03.ContractError('Assessment completion owner mismatch')
            if value.get('completed_at') != r03.utc_instant(source.completed_at, 'completed_at'):
                raise r03.ContractError('Assessment terminal instant mismatch')
            expected = source.evidence.events if 'event_kind' in value else source.evidence.facts
            expected = [canonical_event(e) if 'event_kind' in e else r03a.validate_completion_fact(e) for e in expected]
            if value not in expected or value['skill_id'] not in {s[0] for s in source.skills}:
                raise r03.ContractError('Evidence disagrees with frozen Assessment authority')
        for f in facts:
            source = sources[f['attempt_id']]
            outcome, independent = next((o, i) for code, o, i in source.skills if code == f['skill_id'])
            if (f['outcome'], f['independent_correct']) != (outcome, independent):
                raise r03.ContractError('Completion eligibility mismatch')
        authorities = {a: {'version_id': s.version_id, 'mapped': [c for c, _, _ in s.skills]} for a, s in sources.items()}
        return self._write(session, events, facts, authorities)

    def _write(self, session, events, facts, authorities, *, legacy=False):
        mapping = self.skills(session, {v['skill_id'] for v in events + facts})
        affected, numeric_changed, duplicates = set(), set(), 0
        for value in events + facts:
            if value.get('attempt_id') and value.get('completed_at'):
                a = authorities[value['attempt_id']]
                binding = dict(attempt_id=value['attempt_id'], user_id=int(value['user_id']),
                    completed_at=instant(value['completed_at']), version_id=a['version_id'])
                old = session.execute(sa.select(attempt_binding).where(attempt_binding.c.attempt_id == value['attempt_id'])).first()
                if old and any(getattr(old, k) != v for k, v in binding.items()):
                    raise r03.IdentityConflict('Attempt owner/time/version conflict')
                if old is None:
                    session.execute(attempt_binding.insert().values(**binding))
        for f in facts:
            owner, sid = int(f['user_id']), mapping[f['skill_id']]
            authority = authorities[f['attempt_id']]
            binding = dict(attempt_id=f['attempt_id'], user_id=owner, completed_at=instant(f['completed_at']), version_id=authority['version_id'])
            old = session.execute(sa.select(attempt_binding).where(attempt_binding.c.attempt_id == f['attempt_id'])).first()
            if old and any(getattr(old, k) != v for k, v in binding.items()):
                raise r03.IdentityConflict('Attempt owner/time/version conflict')
            if old is None:
                session.execute(attempt_binding.insert().values(**binding))
            previous = session.execute(sa.select(completion).where(sa.or_(completion.c.completion_id == UUID(f['completion_id']),
                sa.and_(completion.c.attempt_id == f['attempt_id'], completion.c.skill_id == sid)))).all()
            if previous:
                if any(row.payload != f for row in previous):
                    raise r03.IdentityConflict('Global completion identity/source conflict')
                duplicates += 1
                continue
            context = authority.get('contexts', {}).get(f['completion_id']) or {'context_version': 'legacy-completion-v1' if legacy else 'assessment-completion-v1',
                'records': [{'fact': f, 'attempt_state': 'LEGACY_COMPLETION' if legacy else 'COMPLETED',
                             'mapped_skill_ids': authority['mapped']}]}
            r03a._authority_records(context)
            session.execute(completion.insert().values(completion_id=UUID(f['completion_id']), user_id=owner,
                skill_id=sid, attempt_id=f['attempt_id'], completed_at=instant(f['completed_at']),
                policy_version=f['policy_version'], payload=f, authority=context, received_at=utc_now()))
            affected.add((owner, sid))
        for e in events:
            owner, sid = int(e['user_id']), mapping[e['skill_id']]
            source = r03.source_identity(e)
            query = event.c.event_id == e['event_id']
            if source:
                query = sa.or_(query, sa.and_(event.c.attempt_id == source[0], event.c.skill_id == sid,
                    event.c.event_kind == source[2], event.c.evidence_ref == source[3]))
            previous = session.execute(sa.select(event.c.payload).where(query)).scalars().all()
            if previous:
                if any(p != e for p in previous):
                    raise r03.IdentityConflict('Global event identity/source conflict')
                duplicates += 1
                continue
            session.execute(event.insert().values(event_id=e['event_id'], user_id=owner, skill_id=sid,
                attempt_id=e.get('attempt_id'), event_kind=e['event_kind'], evidence_ref=e.get('evidence_ref'),
                occurred_at=instant(e['occurred_at']), policy_version=e['policy_version'], payload=e, received_at=utc_now()))
            affected.add((owner, sid)); numeric_changed.add((owner, sid))
        projections = {f'{u}:{sid}': self._scope(session, u, sid, numerical_changed=(u, sid) in numeric_changed)
                       for u, sid in sorted(affected, key=lambda pair: (pair[0], str(pair[1])))}
        return {'duplicates': duplicates, 'projections': projections}

    def replay(self, session, user_id, skill_code, *, policy='progress-v1.1'):
        sid = self.skills(session, {skill_code})[skill_code]
        locks(session, [f'3:scope:{user_id}:{skill_code}'])
        if policy == 'progress-v1':
            log = list(session.scalars(sa.select(event.c.payload).where(event.c.user_id == user_id, event.c.skill_id == sid)))
            return r03.replay(log, str(user_id), skill_code)
        if policy != 'progress-v1.1':
            raise r03.ContractError('Unregistered reducer policy')
        return self._scope(session, user_id, sid, force=True)

    def import_legacy(self, session, delivery, authority):
        with session.begin_nested():
            return self._import_legacy(session, delivery, authority)

    def _import_legacy(self, session, delivery, authority):
        """Explicit reviewed maintenance input. No IDs/facts are inferred from events."""
        if authority.get('context_version') != 'legacy-completion-v1':
            raise r03.ContractError('Explicit legacy authority required')
        events, facts = [canonical_event(e) for e in delivery.events], [r03a.validate_completion_fact(f) for f in delivery.facts]
        contexts = r03a._authority_records(authority)
        if sorted(facts, key=encoded) != sorted(contexts, key=encoded):
            raise r03.ContractError('Legacy facts require exact authoritative provenance')
        scopes = {(int(v['user_id']), v['skill_id']) for v in events + facts}
        locks(session, ['0:attempt:' + v['attempt_id'] for v in facts]
              + ['1:event:' + e['event_id'] for e in events]
              + ['2:completion:' + f['completion_id'] for f in facts]
              + [f'3:scope:{u}:{s}' for u, s in scopes])
        for user, code in scopes:
            r03a.import_progress_v1_completions(events, str(user), code, authority=authority)
        authorities = {}
        for record in authority['records']:
            f = r03a.validate_completion_fact(record['fact'])
            a = authorities.setdefault(f['attempt_id'], {'version_id': 'legacy-progress-v1', 'mapped': [], 'contexts': {}})
            a['mapped'] = sorted(set(a['mapped']) | set(record['mapped_skill_ids']))
            a['contexts'][f['completion_id']] = {'context_version': 'legacy-completion-v1', 'records': [record]}
        return self._write(session, events, facts, authorities, legacy=True)

    def self_report(self, session, user_id, codes):
        with session.begin_nested():
            return self._self_report(session, user_id, codes)

    def _self_report(self, session, user_id, codes):
        mapping = self.skills(session, codes)
        if set(session.scalars(sa.select(skill.c.code).where(skill.c.code.in_(codes), skill.c.active.is_(True)))) != set(codes):
            raise r03.ContractError('Self-report skill must be active')
        locks(session, [f'3:scope:{user_id}:{code}' for code in codes])
        accepted, existing = [], []
        for code in sorted(codes):
            sid = mapping[code]
            log = list(session.scalars(sa.select(event.c.payload).where(event.c.user_id == user_id, event.c.skill_id == sid)))
            has_completion = session.scalar(sa.select(sa.exists(sa.select(completion.c.completion_id).where(
                completion.c.user_id == user_id, completion.c.skill_id == sid))))
            if any(e['event_kind'] == 'SELF_REPORTED_KNOWN' for e in log):
                existing.append(code)
            elif has_completion or any(e['event_kind'] in r03.ASSESSED_KINDS for e in log):
                raise r03.ContractError('Self-report after assessed evidence is forbidden')
            else:
                e = canonical_event(dict(event_id=str(uuid4()), user_id=str(user_id), skill_id=code,
                    event_kind='SELF_REPORTED_KNOWN', occurred_at=utc_now().isoformat(timespec='microseconds').replace('+00:00', 'Z'),
                    policy_version='progress-v1'))
                self._write(session, [e], [], {})
                accepted.append(code)
        return {'accepted_skill_codes': accepted, 'already_reported_skill_codes': existing}
