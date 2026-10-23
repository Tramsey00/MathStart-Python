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
    parser.add_argument('action', choices=['check-sources', 'check-lesson-sources', 'check-content-quality', 'check-site-integrity', 'index-lessons', 'bootstrap', 'build-inputs'])
    parser.add_argument('--source-root', type=Path, default=Path('.'))
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--release-id')
    parser.add_argument('--release-root', type=Path)
    parser.add_argument('--source-sha')
    parser.add_argument('--disposable', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--slug', nargs='+')
    selection.add_argument('--all', dest='all_lessons', action='store_true')
    parser.add_argument('--origin')
    parser.add_argument('--report-root', type=Path)
    parser.add_argument('--static-root', type=Path, action='append')
    parser.add_argument('--media-root', type=Path)
    args = parser.parse_args(argv)
    engine = None
    exit_code = 0
    try:
        root = args.source_root.resolve()
        if args.action == 'check-sources':
            bundles = load_sources(root)
            result = {'pages': len(bundles), 'topics': sum(b.snapshot['page_type'] == 'topic' for b in bundles)}
        else:
            engine = create_engine(DatabaseConfig.from_environment())
            with UnitOfWork(engine) as uow:
                if args.action == 'index-lessons':
                    if not args.output_root or args.slug or args.all_lessons:
                        parser.error('index-lessons requires output-root and always indexes all lessons')
                    if engine.dialect.name == 'postgresql':
                        uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
                    from backend.content.indexing import index_bytes, write_index
                    payload, count = index_bytes(uow.session, root)
                    result = {'indexed': count, 'effects': write_index(args.output_root, payload, dry_run=args.dry_run)}
                elif args.action in {'check-lesson-sources', 'check-content-quality', 'check-site-integrity'}:
                    if args.dry_run:
                        parser.error('inspection commands have no dry-run; reports are an explicit file effect')
                    if engine.dialect.name == 'postgresql':
                        uow.session.execute(sa.text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY'))
                    from backend.content.checks import verify_lesson_sources, inspect_site, inspect_public_quality
                    if args.action == 'check-lesson-sources':
                        result = verify_lesson_sources(uow.session, root, slugs=args.slug, all_lessons=args.all_lessons)
                    else:
                        if not args.report_root:
                            parser.error('quality/integrity inspections require explicit report-root')
                        if args.action == 'check-site-integrity':
                            if not args.static_root or not args.media_root:
                                parser.error('site integrity requires static-root and media-root')
                            report, errors = inspect_site(uow.session, static_roots=args.static_root, media_root=args.media_root)
                            report_name = 'site_integrity_report.json'
                        else:
                            if not args.origin:
                                parser.error('content quality requires the running public origin')
                            from backend.content.checks import active_quality_release
                            release = active_quality_release(uow.session, args.release_root) if args.release_root else None
                            report, errors = inspect_public_quality(uow.session, args.origin, release=release)
                            report_name = 'content_quality_report.json'
                        args.report_root.mkdir(parents=True, exist_ok=True)
                        (args.report_root / report_name).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                        result = {'report': report_name, 'errors': errors,
                                  **({'summary': report['summary']} if 'summary' in report else {k: v for k, v in report.items() if k != 'issues'})}
                        exit_code = 1 if errors else 0
                elif args.action == 'bootstrap':
                    if not args.disposable:
                        parser.error('fixture bootstrap requires --disposable; use prepare-bootstrap for fenced publication')
                    require_disposable(uow.session.connection())
                    if args.dry_run:
                        if not args.source_sha:
                            parser.error('bootstrap dry-run requires an explicit reviewed source-sha')
                        from backend.content.preparation import prepare_sources
                        result = prepare_sources(engine, root, None, args.release_id or 'bootstrap-preview',
                            args.source_sha, bootstrap=True, dry_run=True)
                    else:
                        from backend.users.bootstrap import seed_permissions
                        seed_permissions(uow.session)
                        bundles = bootstrap_sources(uow.session, root)
                        uow.commit()
                        result = {'pages': len(bundles), 'transaction': 'COMMITTED',
                                  'sequence_side_effects': 'normal committed inserts'}
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
        return exit_code
    except Exception as error:
        # Do not expose SQL parameters, DSNs, private payloads or operator paths.
        print('Target command refused/failed: ' + type(error).__name__, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
