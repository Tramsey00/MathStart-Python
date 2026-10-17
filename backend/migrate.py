"""Explicit, guarded local rehearsal CLI. No production operation mode."""
import argparse
import sys
from backend.infrastructure.database import DatabaseConfig, create_engine, DatabaseUnavailable
from backend.migrations.upgrade import fresh, upgrade_profile
from backend.migrations.schema import SchemaMismatch, assert_baseline
import sqlalchemy as sa


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['fresh', 'upgrade', 'check'])
    parser.add_argument('--profile', choices=['A', 'B', 'C'])
    parser.add_argument('--disposable', action='store_true', required=True)
    parser.add_argument('--reviewed-rehearsal', action='store_true')
    args = parser.parse_args(argv)
    engine = None
    try:
        engine = create_engine(DatabaseConfig.from_environment())
        with engine.begin() as connection:
            if args.action == 'fresh':
                fresh(connection)
            elif args.action == 'upgrade':
                if args.profile is None:
                    parser.error('--profile is required for upgrade')
                upgrade_profile(connection, args.profile, reviewed=args.reviewed_rehearsal)
            else:
                from backend.migrations.upgrade import require_disposable
                require_disposable(connection)
                assert_baseline(connection, args.profile or 'B', allow_protocol=True, require_history=False)
        print('V01 ' + args.action + ' completed on explicitly selected disposable backend')
        return 0
    except (sa.exc.DBAPIError, DatabaseUnavailable, SchemaMismatch, ValueError, RuntimeError) as error:
        # SQL exception details/parameters may include credentials or hashes.
        print('V01 operation refused/failed: ' + type(error).__name__, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
