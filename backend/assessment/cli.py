"""Preview, import, publish or archive the reviewed exercise bank explicitly."""
import argparse
import hmac
import json
from pathlib import Path
import sys

import sqlalchemy as sa

from backend.infrastructure.database import DatabaseConfig, create_engine

from .bank import apply_bank, archive
from .package import BankError, code_value, read_package


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    for action in ('preview', 'import', 'publish'):
        command = actions.add_parser(action)
        command.add_argument('--package', type=Path, required=True)
        if action != 'preview':
            command.add_argument('--reviewed-sha256', required=True)
    command = actions.add_parser('archive')
    command.add_argument('exercise_code')
    command.add_argument('version', type=int)
    args = parser.parse_args(argv)
    engine = None
    try:
        receipt = {'action': args.action}
        if args.action != 'archive':
            rows, coverage, package_sha = read_package(args.package)
            receipt.update(coverage=coverage, package_sha256=package_sha)
            if args.action != 'preview' and not hmac.compare_digest(package_sha, args.reviewed_sha256):
                raise BankError('Reviewed package SHA-256 does not match')
        if args.action != 'preview':
            engine = create_engine(DatabaseConfig.from_environment())
            if engine.dialect.name != 'postgresql':
                raise BankError('Assessment bank requires PostgreSQL')
            if args.action == 'archive':
                if not code_value(args.exercise_code) or not 1 <= args.version < 2**31:
                    raise BankError('Invalid exercise code or version')
                receipt.update(exercise_code=args.exercise_code, version=args.version,
                               changed=archive(engine, args.exercise_code, args.version))
            else:
                receipt['changed'] = apply_bank(engine, rows, args.action)
    except BankError as error:
        print('ASSESSMENT_BANK_REFUSED: ' + str(error), file=sys.stderr)
        return 1
    except (sa.exc.SQLAlchemyError, OSError, ValueError, RecursionError) as error:
        print('ASSESSMENT_BANK_REFUSED_OR_UNCERTAIN: ' + type(error).__name__, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
