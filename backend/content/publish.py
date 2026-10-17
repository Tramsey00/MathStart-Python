"""Operator publication/recovery CLI; no HTTP writer or Django dependency.

Prepared content changes and immutable input/React build handoffs are
reviewable before claim. Recovery resumes the durable plan, never reruns a
committed domain update or switches an older completed operation back on.
"""
import argparse
from contextlib import contextmanager
from dataclasses import asdict
import json
from pathlib import Path
import sys
import threading
import uuid

import sqlalchemy as sa

from backend.content.build import encoded
from backend.content.editions import snapshot, project_updates
from backend.content.participant import PreparedPublication, PrecommitProof, NoDomainWork, digest
from backend.content.publication import PublisherAuthority, PublicationConflict, OwnerToken, descriptor
from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.http.transport import decode_json
from backend.infrastructure.uow import UnitOfWork
from backend.models.protocol import ActiveReleaseDescriptor, PublicationJournal, PublicationGate


@contextmanager
def keep_lease(authority, token):
    stop = threading.Event()
    def renew():
        while not stop.wait(authority.lease.total_seconds() / 3):
            try:
                authority.renew(token)
            except Exception:
                return
    thread = threading.Thread(target=renew, name='publication-lease', daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set(); thread.join(timeout=35)
        if thread.is_alive():
            raise PublicationConflict('LEASE_WORKER_FAILED')
        # Every mutating authority call independently fences stale work. No
        # heartbeat failure can manufacture a successful completion.


def finish(authority, token):
    """Only the journal determines the next step; unknown states fail closed."""
    observed = authority.inspect(token)
    if observed['phase'] == 'COMPLETE':
        return authority.complete(token)
    if observed['phase'] == 'FAILED_PRECOMMIT':
        return authority.fail_precommit(token)
    with keep_lease(authority, token):
        for _ in range(9):
            phase = authority.inspect(token)['phase']
            if phase in {'COMPLETE', 'FAILED_PRECOMMIT'}:
                return authority.complete(token) if phase == 'COMPLETE' else authority.fail_precommit(token)
            if phase in {'VALIDATED', 'STAGED'}:
                authority.stage(token)
                authority.commit(token)
            elif phase == 'DB_COMMITTED':
                authority.intent(token)
            elif phase == 'ACTIVATING':
                authority.activate(token)
            elif phase == 'ACTIVATED':
                return authority.complete(token)
            elif phase == 'RECOVERY_REQUIRED':
                authority.reconcile(token)
            else:
                raise PublicationConflict('INVALID_PHASE')
    raise PublicationConflict('RECOVERY_REQUIRED')


def plan_candidate(engine, args):
    prepared = decode_json(args.changes.read_bytes())
    changes = prepared['changes'] if isinstance(prepared, dict) else prepared
    manifest = decode_json((args.output_root / 'output-manifest.json').read_bytes())
    with UnitOfWork(engine) as uow:
        uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
        before = snapshot(uow.session)
        previous = descriptor(uow.session.get(ActiveReleaseDescriptor, args.namespace))
    after = project_updates(before, changes)
    if isinstance(prepared, dict) and (set(prepared) != {'version', 'before_digest', 'after_digest', 'changes'}
            or prepared['version'] != 'prepared-source-edition-v1' or prepared['before_digest'] != digest(before)
            or prepared['after_digest'] != digest(after)):
        raise PublicationConflict('SOURCE_CONFLICT')
    plan = {'version': 'prepared-publication-v1', 'kind': args.kind,
            'release_id': manifest['release_id'], 'manifest_digest': manifest['input_manifest_digest'],
            'input_receipt_digest': manifest['input_receipt_digest'],
            'output_manifest_digest': args.output_digest, 'origin': args.origin,
            'previous': previous, 'changes': changes, 'before_digest': digest(before), 'after_digest': digest(after)}
    # No staging files, DB changes, gate claim or sequence allocation here.
    PreparedPublication(plan, input_root=args.input_root, output_root=args.output_root,
                        release_root=args.release_root, artifact_root=args.artifact_root)
    with args.plan.open('xb') as stream:
        stream.write(encoded(plan))
    return {'plan_digest': digest(plan), 'release_id': plan['release_id'], 'activation': 'NOT_PERFORMED',
            'effects': 'exclusive plan file only; no DB or sequence writes'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare-sources', 'prepare-bootstrap', 'plan', 'publish', 'unpublish', 'status', 'resume', 'recover', 'abort', 'renew', 'surrender'])
    parser.add_argument('--namespace', default='public')
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--changes', type=Path)
    parser.add_argument('--source-root', type=Path, default=Path('.'))
    parser.add_argument('--source-sha')
    parser.add_argument('--release-id')
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--slug', nargs='+')
    selection.add_argument('--all', dest='all_lessons', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--kind', choices=['publish', 'unpublish'], default='publish')
    parser.add_argument('--input-root', type=Path)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--output-digest')
    parser.add_argument('--release-root', type=Path)
    parser.add_argument('--artifact-root', type=Path)
    parser.add_argument('--origin')
    parser.add_argument('--key')
    parser.add_argument('--owner', type=uuid.UUID)
    parser.add_argument('--operation-id', type=uuid.UUID)
    parser.add_argument('--generation', type=int)
    parser.add_argument('--lease-seconds', type=int, default=120)
    args = parser.parse_args(argv)
    if args.dry_run and args.action not in {'prepare-sources', 'prepare-bootstrap'}:
        parser.error('only source/bootstrap preparation supports a read-only dry-run')
    engine, token = None, None
    try:
        engine = create_engine(DatabaseConfig.from_environment())
        if engine.dialect.name != 'postgresql':
            raise PublicationConflict('POSTGRESQL_REQUIRED')
        if args.action in {'prepare-sources', 'prepare-bootstrap'}:
            if not args.source_sha or not args.release_id or (not args.dry_run and (not args.input_root or not args.changes)):
                parser.error('preparation requires source-sha/release-id, and input-root/changes destination unless dry-run')
            if not args.dry_run and args.changes.exists():
                raise PublicationConflict('EXISTING_HANDOFF')
            from backend.content.preparation import prepare_sources
            result = prepare_sources(engine, args.source_root, args.input_root, args.release_id, args.source_sha,
                        slugs=args.slug, all_lessons=args.all_lessons, unpublish=args.kind == 'unpublish',
                        dry_run=args.dry_run, bootstrap=args.action == 'prepare-bootstrap')
            if not args.dry_run:
                handoff = {'version': 'prepared-source-edition-v1', **{key: result[key] for key in ('before_digest', 'after_digest', 'changes')}}
                with args.changes.open('xb') as stream:
                    stream.write(encoded(handoff))
                result['changes'] = len(result['changes'])
        elif args.action == 'status':
            with UnitOfWork(engine) as uow:
                uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
                gate = uow.session.get(PublicationGate, args.namespace)
                row = uow.session.get(PublicationJournal, args.operation_id or (gate.pending_operation_id if gate else None)) if args.operation_id or gate and gate.pending_operation_id else None
                if row is not None and row.namespace != args.namespace:
                    raise PublicationConflict('MISSING_OPERATION')
                result = {'active': descriptor(uow.session.get(ActiveReleaseDescriptor, args.namespace)),
                          'operation': None if row is None else {'operation_id': str(row.id), 'owner_id': str(row.owner_id),
                          'generation': row.fence_generation, 'phase': row.phase, 'db_committed': row.db_committed,
                          'activation_status': row.activation_status, 'error_code': row.error_code}}
        else:
            roots = () if args.action in {'renew', 'surrender', 'resume'} else ('release_root',) if args.action == 'abort' else ('input_root', 'output_root', 'release_root', 'artifact_root')
            for name in roots:
                if getattr(args, name) is None:
                    parser.error('explicit input/output handoff and installed release/artifact roots required')
            if args.action == 'plan':
                if not all([args.plan, args.changes, args.origin, args.output_digest]):
                    parser.error('plan requires changes, plan destination, origin and trusted output digest')
                result = plan_candidate(engine, args)
            else:
                if args.owner is None:
                    parser.error('explicit stable owner UUID required')
                if args.action in {'publish', 'unpublish'}:
                    if args.plan is None or not args.key:
                        parser.error('publish/unpublish require reviewed plan and idempotency key')
                    plan = decode_json(args.plan.read_bytes())
                    if plan['kind'] != args.action:
                        raise PublicationConflict('INVALID_PLAN')
                else:
                    if args.operation_id is None or args.generation is None:
                        parser.error('explicit operation-id and observed/current generation required')
                    with UnitOfWork(engine) as uow:
                        uow.session.execute(sa.text('SET TRANSACTION READ ONLY'))
                        row = uow.session.get(PublicationJournal, args.operation_id)
                        if row is None or row.namespace != args.namespace:
                            raise PublicationConflict('MISSING_OPERATION')
                        plan = row.plan
                        observed_phase = row.phase
                if args.action in {'renew', 'surrender'} or args.action == 'resume' and observed_phase in {'COMPLETE', 'FAILED_PRECOMMIT'}:
                    participant = NoDomainWork()
                elif args.action == 'abort':
                    participant = PrecommitProof(plan, args.release_root)
                else:
                    if any(value is None for value in (args.input_root, args.output_root, args.release_root, args.artifact_root)):
                        parser.error('nonterminal publication needs explicit immutable handoff and installed roots')
                    participant = PreparedPublication(plan, input_root=args.input_root, output_root=args.output_root,
                        release_root=args.release_root, artifact_root=args.artifact_root)
                authority = PublisherAuthority(engine, participant, lease_seconds=args.lease_seconds)
                if args.action in {'publish', 'unpublish'}:
                    token, _ = authority.claim(args.namespace, args.key, plan, args.owner)
                elif args.action == 'recover':
                    token = authority.takeover(args.namespace, args.operation_id, args.generation, args.owner)
                else:
                    token = OwnerToken(args.namespace, args.operation_id, args.owner, args.generation)
                if args.action == 'abort':
                    phase = authority.fail_precommit(token)
                elif args.action in {'renew', 'surrender'}:
                    authority.renew(token, surrender=args.action == 'surrender')
                    phase = authority.inspect(token)['phase']
                else:
                    phase = finish(authority, token)
                    if phase != 'COMPLETE':
                        raise PublicationConflict('FAILED_PRECOMMIT')
                result = {'token': {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in asdict(token).items()}, 'phase': phase}
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as error:
        code = error.code if isinstance(error, PublicationConflict) else type(error).__name__
        print(json.dumps({'error': code, 'operation_id': str(token.operation_id) if token else None}), file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
