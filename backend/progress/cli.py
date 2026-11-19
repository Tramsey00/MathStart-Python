"""Explicit owner/skill replay and reviewed legacy import; never run at startup."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.uow import UnitOfWork
from .contracts import Delivery
from .service import ProgressService


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    replay = subs.add_parser('replay')
    replay.add_argument('--user-id', type=int, required=True)
    replay.add_argument('--skill-code', required=True)
    replay.add_argument('--policy', choices=['progress-v1','progress-v1.1'], default='progress-v1.1')
    replay.add_argument('--apply', action='store_true')
    legacy = subs.add_parser('import-legacy')
    legacy.add_argument('--file', type=Path, required=True)
    legacy.add_argument('--reviewed-sha256', required=True)
    args = parser.parse_args()
    engine = create_engine(DatabaseConfig.from_environment())
    try:
        with UnitOfWork(engine) as uow:
            service = ProgressService()
            if args.action == 'replay':
                result = service.replay(uow.session, args.user_id, args.skill_code, policy=args.policy)
                if args.apply:
                    if args.policy != 'progress-v1.1': raise ValueError('Legacy replay is read-only')
                    uow.commit()
                print(json.dumps(result, sort_keys=True))
            else:
                raw = args.file.read_bytes()
                if sha256(raw).hexdigest() != args.reviewed_sha256: raise ValueError('Reviewed input digest mismatch')
                from backend.infrastructure.json_input import decode_json
                data = decode_json(raw)
                service.import_legacy(uow.session, Delivery(events=data['events'], facts=data['facts']), data['authority'])
                uow.commit()
                print('IMPORTED: retained immutable legacy identities; exact numerical parity verified')
    finally:
        engine.dispose()


if __name__ == '__main__':
    main()
