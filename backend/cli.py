"""Explicit target content commands; ordinary execution never imports Django."""
import argparse
import json
from pathlib import Path
import sys

import sqlalchemy as sa

from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.upgrade import require_disposable
from backend.content.sources import load_sources
from backend.content.bootstrap import bootstrap_sources
from backend.content.build import write_build_inputs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check-sources', 'bootstrap', 'build-inputs'])
    parser.add_argument('--source-root', type=Path, default=Path('.'))
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--release-id')
    parser.add_argument('--source-sha')
    parser.add_argument('--disposable', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    engine = None
    try:
        root = args.source_root.resolve()
        if args.action == 'check-sources':
            bundles = load_sources(root)
            result = {'pages': len(bundles), 'topics': sum(b.snapshot['page_type'] == 'topic' for b in bundles)}
        else:
            engine = create_engine(DatabaseConfig.from_environment())
            with UnitOfWork(engine) as uow:
                if args.action == 'bootstrap':
                    if not args.disposable:
                        parser.error('bootstrap currently requires --disposable')
                    require_disposable(uow.session.connection())
                    bundles = bootstrap_sources(uow.session, root)
                    if not args.dry_run:
                        uow.commit()
                    result = {'pages': len(bundles), 'transaction': 'ROLLED_BACK' if args.dry_run else 'COMMITTED',
                              'sequence_side_effects': 'possible even in dry-run'}
                else:
                    if not args.output_root or not args.release_id or not args.source_sha:
                        parser.error('build-inputs requires output-root, release-id and source-sha')
                    if args.dry_run:
                        parser.error('build-inputs has no dry-run; use check-sources')
                    if engine.dialect.name == 'postgresql':
                        uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
                    _, result = write_build_inputs(uow, root, args.output_root, args.release_id, args.source_sha)
                    result = {k: v for k, v in result.items() if k not in {'files', 'source_files'}}
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as error:
        # Do not expose SQL parameters, DSNs, private payloads or operator paths.
        print('Target command refused/failed: ' + type(error).__name__, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
