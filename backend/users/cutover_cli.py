"""Preview/apply a reviewed private cutover plan; no role changes or deletion."""
import argparse
import json
import os
from pathlib import Path

from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.users.cutover import CutoverImport


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preview', 'apply'])
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--checkpoint-id')
    args = parser.parse_args(argv)
    engine = None
    try:
        key = os.environ['MATHSTART_HTTP_SIGNING_KEY']
        fallbacks = json.loads(os.environ.get('MATHSTART_HTTP_SIGNING_FALLBACK_KEYS', '[]'))
        if not isinstance(fallbacks, list):
            raise ValueError('Explicit keyring required')
        engine = create_engine(DatabaseConfig.from_environment())
        service = CutoverImport(engine, (key, *fallbacks), os.environ['MATHSTART_LEGACY_WRITER_ROLE'])
        if args.action == 'preview':
            plan = service.preview(args.checkpoint_id)
            # Exclusive creation prevents replacing an already reviewed plan.
            with args.plan.open('x', encoding='utf-8', newline='\n') as output:
                output.write(json.dumps(plan, indent=2) + '\n')
                output.flush()
                os.fsync(output.fileno())
            print(json.dumps({'status': 'PREVIEW', **plan}))
        else:
            result = service.apply(json.loads(args.plan.read_text(encoding='utf-8')))
            print(json.dumps({'status': 'APPLIED', **result}))
        return 0
    except Exception:
        # DB errors/source data/DSN are private; no exception text is emitted.
        print(json.dumps({'status': 'REFUSED', 'code': 'CUTOVER_RECONCILIATION_REQUIRED'}))
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
