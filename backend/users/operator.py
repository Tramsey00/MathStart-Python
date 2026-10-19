"""Create the first fresh operator explicitly; never reset/adopt an existing user.

Credentials come from a private environment only with --from-environment, or
from non-echoing prompts. This command is not run by startup or schema migration.
"""
import argparse
import getpass
import os
import sys
import unicodedata

import sqlalchemy as sa

from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.infrastructure.uow import UnitOfWork
from backend.migrations.schema import SchemaMismatch, assert_baseline
from backend.models.baseline import User, StudentProfile, metadata
from backend.users import passwords
from backend.users.bootstrap import seed_permissions
from backend.users.cutover import outer_lock


def create_initial(engine, username, password, email='', *, maintenance=False):
    if not maintenance or not isinstance(username, str) or not isinstance(password, str) or not isinstance(email, str):
        raise ValueError('Explicit maintenance and valid operator credentials required')
    username = unicodedata.normalize('NFKC', username)
    user = User(username=username, email=email, is_active=True, is_staff=True, is_superuser=True)
    if (not passwords.valid_username(username) or not passwords.valid_email(email)
            or not 8 <= len(password) <= 512 or not passwords.validate_password(password, user)):
        raise ValueError('Operator credentials do not satisfy the retained validators')
    user.password = passwords.encode(password)
    with UnitOfWork(engine) as uow:
        session = uow.session
        if engine.dialect.name != 'postgresql' or int(session.scalar(sa.text('SHOW server_version_num'))) < 160000:
            raise SchemaMismatch('Fresh operator provisioning requires PostgreSQL16+')
        outer_lock(session, exclusive=True)
        if session.scalar(sa.text('''SELECT EXISTS(SELECT 1 FROM pg_stat_activity
                WHERE datid=(SELECT oid FROM pg_database WHERE datname=current_database())
                AND pid<>pg_backend_pid() AND backend_type='client backend')''')):
            raise SchemaMismatch('Disconnect all other clients for initial operator maintenance')
        assert_baseline(session.connection(), 'B', allow_protocol=True, require_history=False)
        # Empty user table alone cannot distinguish a fresh install from legacy
        # history or prior target traffic. Never bootstrap over any such state.
        for name in ('auth_user', 'users_studentprofile', 'django_migrations', 'django_session',
                     'users_identityreceipt', 'users_loginwindow', 'target_session',
                     'target_receipt_bridge', 'target_identity_cutover'):
            if session.scalar(sa.select(sa.exists(sa.select(metadata.tables[name])))):
                raise SchemaMismatch('Initial operator requires a fresh unused identity database')
        seed_permissions(session)
        session.add(user); session.flush()
        session.add(StudentProfile(user_id=user.id, onboarding_complete=False,
                                   onboarding_mode=None, selected_grade_id=None))
        uow.commit()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--maintenance', action='store_true', required=True)
    parser.add_argument('--from-environment', action='store_true')
    args = parser.parse_args(argv)
    engine = None
    try:
        if args.from_environment:
            username = os.environ['MATHSTART_OPERATOR_USERNAME']
            password = os.environ['MATHSTART_OPERATOR_PASSWORD']
            email = os.environ.get('MATHSTART_OPERATOR_EMAIL', '')
        else:
            username = getpass.getpass('Initial operator username: ')
            email = getpass.getpass('Email (optional): ')
            password = getpass.getpass('Password: ')
            if password != getpass.getpass('Repeat password: '):
                raise ValueError('Passwords differ')
        engine = create_engine(DatabaseConfig.from_environment())
        create_initial(engine, username, password, email, maintenance=args.maintenance)
        print('INITIAL_OPERATOR_CREATED: retained password policy; fresh staff/superuser and profile')
        return 0
    except Exception as error:
        # An uncertain COMMIT is not success. Existing user state blocks replay;
        # retain maintenance and reconcile privately, never reset automatically.
        print('OPERATOR_REFUSED_OR_UNCERTAIN: ' + type(error).__name__, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
