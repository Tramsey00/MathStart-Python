"""R03 result observer for unchanged owner cases and runtime; not owner code."""
import argparse
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest


def save(path, value):
    path.write_bytes((json.dumps(value, indent=2, default=str)+'\n').encode())


def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case


def suite_run(kind, candidate, output, successor=None):
    sys.path.insert(0, str(candidate))
    loader = unittest.TestLoader()
    if kind == 'v02':
        modules = ['backend.tests.v02.'+name for name in ('test_unit', 'test_http', 'test_postgres', 'test_asset_regressions')]
        suite = loader.loadTestsFromNames(modules)
        if successor is None:
            matrix = json.loads((candidate/'docs/acceptance/MS7-MIG-V02/remediation-f01-f02/test-matrix.json').read_bytes())
            expected_ids = {row['test'] for row in matrix['named_tests']}
            expected, expected_pg = 86, 40
        else:
            expected_ids = set(successor['v02_case_ids'])
            expected, expected_pg = 118, 50
            if len(expected_ids) != expected:
                raise RuntimeError('EXACT_REVIEWED_SUCCESSOR_CASES')
        pg_test = lambda name: '.PostgreSQL' in name
    elif kind == 'v01':
        modules = ['backend.tests.'+name for name in ('test_unit', 'test_postgres', 'test_remediation')]
        suite = loader.loadTestsFromNames(modules)
        matrix = json.loads((candidate/'docs/acceptance/MS7-MIG-V01/target-ci-cases-v5.json').read_bytes())
        expected_ids = {row['id'] for row in matrix['cases']}
        expected, expected_pg = 34, 23
        pg_test = lambda name: '.test_postgres.' in name or '.test_remediation.' in name
    else:
        pattern, expected = {'r02': ('test_migration_r02*.py', 63),
                             'r02a': ('test_r02a_contract.py', 30),
                             'r03a': ('test_r03a_contract.py', 41)}[kind]
        suite = loader.discover(str(candidate/'tests'), pattern=pattern)
        expected_ids, expected_pg = None, 0
        pg_test = lambda name: False
    cases = list(flatten(suite))
    ids = [case.id() for case in cases]
    pg = [name for name in ids if pg_test(name)]
    save(output/(kind+'-collected.json'), dict(ids=ids, count=len(ids), pg_count=len(pg), loader_errors=loader.errors))
    if loader.errors or len(ids) != expected or len(set(ids)) != expected or len(pg) != expected_pg:
        raise RuntimeError('NONEMPTY_EXACT_CASE_INVENTORY: '+kind)
    if expected_ids is not None and set(ids) != expected_ids:
        raise RuntimeError('OWNER_CASE_INVENTORY_DIFF: '+kind)
    events = []

    class Result(unittest.TextTestResult):
        def startTest(self, test):
            events.append(dict(id=test.id(), result='RUNNING', subtests=[]))
            super().startTest(test)

        def addSuccess(self, test):
            events[-1]['result'] = 'PASS'
            super().addSuccess(test)

        def addFailure(self, test, error):
            events[-1]['result'] = 'FAIL'
            super().addFailure(test, error)

        def addError(self, test, error):
            events[-1]['result'] = 'ERROR'
            super().addError(test, error)

        def addSkip(self, test, reason):
            events[-1].update(result='SKIP', reason=reason)
            super().addSkip(test, reason)

        def addSubTest(self, test, subtest, error):
            events[-1]['subtests'].append(dict(id=subtest.id(), result='PASS' if error is None else 'FAIL'))
            super().addSubTest(test, subtest, error)

    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    ok = (result.wasSuccessful() and result.testsRun == expected and not result.skipped and
          not result.expectedFailures and not result.unexpectedSuccesses and
          all(row['result'] == 'PASS' for row in events))
    record = dict(kind=kind, tests_run=result.testsRun, postgres_collected=len(pg), skips=len(result.skipped),
                  failures=len(result.failures), errors=len(result.errors), expected_failures=len(result.expectedFailures),
                  unexpected_successes=len(result.unexpectedSuccesses), case_inventory_matches=True,
                  result='PASS' if ok else 'FAIL', cases=events, python=sys.version,
                  installed={d.metadata['Name']: d.version for d in importlib.metadata.distributions()})
    save(output/(kind+'-tests.json'), record)
    if not ok:
        raise RuntimeError('OWNER_SUITE_FAILED: '+kind)


def db(command, output):
    import sqlalchemy as sa
    if os.environ.get('R03_TASK_SERVICE_ACK') != 'VERIFIED_GITHUB_DISPOSABLE_POSTGRES16':
        raise RuntimeError('OWNED_SERVICE_ACK_REQUIRED')
    port = os.environ['R03_DB_PORT']
    if port not in ('15441', '55441'):
        raise RuntimeError('UNOWNED_SERVICE_PORT')
    engine = sa.create_engine('postgresql+psycopg://postgres@127.0.0.1:'+port+'/postgres',
                              isolation_level='AUTOCOMMIT', hide_parameters=True)
    try:
        with engine.connect() as connection:
            version = connection.exec_driver_sql('SHOW server_version').scalar_one()
            if int(version.split('.')[0]) != 16:
                raise RuntimeError('POSTGRES16_REQUIRED')
            if command == 'create':
                name = os.environ['R03_PROFILE_DB']
                if not name.startswith('ms6_v01_smoke_v02_'):
                    raise RuntimeError('UNOWNED_PROFILE_NAME')
                quoted = engine.dialect.identifier_preparer.quote(name)
                connection.exec_driver_sql('CREATE DATABASE '+quoted)
                connection.exec_driver_sql("COMMENT ON DATABASE "+quoted+" IS 'MS7-MIG-V02 disposable baseline verification'")
            elif command == 'drop':
                name = os.environ['R03_PROFILE_DB']
                marker = connection.exec_driver_sql('SELECT shobj_description(oid, \'pg_database\') FROM pg_database WHERE datname=%s', (name,)).scalar_one()
                if not name.startswith('ms6_v01_smoke_v02_') or marker != 'MS7-MIG-V02 disposable baseline verification':
                    raise RuntimeError('PROFILE_OWNERSHIP_MARKER')
                connection.exec_driver_sql('DROP DATABASE '+engine.dialect.identifier_preparer.quote(name)+' WITH (FORCE)')
            names = list(connection.exec_driver_sql("SELECT datname FROM pg_database WHERE datname NOT IN ('postgres','template0','template1') ORDER BY datname").scalars())
            record = dict(port=port, server_version=version, databases=names, command=command)
            save(output/('db-'+port+'-'+command+'.json'), record)
            if command in ('before', 'after') and names:
                raise RuntimeError('DISPOSABLE_SERVICE_NOT_EMPTY')
    finally:
        engine.dispose()


def runtime(candidate, output):
    sys.path.insert(0, str(candidate))
    for name in ('django', 'rest_framework'):
        if importlib.util.find_spec(name) is not None:
            raise RuntimeError('FORBIDDEN_RUNTIME_PACKAGE: '+name)
    from backend.infrastructure.http.runtime import application
    app = application()
    if len(app.state.implemented_routes) != 32 or any(name == 'django' or name.startswith(('django.', 'rest_framework')) for name in sys.modules):
        raise RuntimeError('RUNTIME_IMPORT_OR_REGISTRY')
    save(output/'runtime-no-django.json', dict(result='PASS', implemented_routes=app.state.implemented_routes,
                                            operations=32, django_installed=False, django_imported=False,
                                            drf_installed=False, python=sys.version,
                                            installed={d.metadata['Name']: d.version for d in importlib.metadata.distributions()}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['v02', 'v01', 'r02', 'r02a', 'r03a', 'db', 'runtime'])
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--db-command', choices=['before', 'after', 'create', 'drop'])
    parser.add_argument('--successor-scope', type=Path)
    parser.add_argument('--scope-sha256')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.kind == 'db':
        db(args.db_command, args.output)
    elif args.kind == 'runtime':
        runtime(args.candidate.resolve(), args.output)
    else:
        successor = None
        if args.successor_scope is not None:
            spec = importlib.util.spec_from_file_location('r03_worker_successor', Path(__file__).with_name('v02_successor_gate.py'))
            guard = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(guard)
            successor = guard.reviewed_scope(args.successor_scope.read_bytes(), args.scope_sha256)
        elif args.scope_sha256 is not None:
            raise RuntimeError('SCOPE_PATH_REQUIRED_WITH_DIGEST')
        suite_run(args.kind, args.candidate.resolve(), args.output, successor)
