"""Record target test/fixture events while executing the unchanged V01 v5 gate.

Only the R03 disposable CI process uses this observer; no owner source is edited.
All unittest callbacks and fixture contexts delegate to their original behavior.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import sys
import unittest


def now():
    return datetime.now(timezone.utc).isoformat()


def save(name, value):
    destination = Path(os.environ['R03_V01_OUTPUT']) / name
    with destination.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')


def probe(name):
    import sqlalchemy as sa
    engine = sa.create_engine(os.environ['MATHSTART_V01_TEST_ADMIN_URL'], hide_parameters=True)
    try:
        with engine.connect() as connection:
            version = connection.exec_driver_sql('SHOW server_version').scalar_one()
            number = int(connection.exec_driver_sql('SHOW server_version_num').scalar_one())
            databases = list(connection.exec_driver_sql(
                "SELECT datname FROM pg_database WHERE datname NOT IN ('postgres','template0','template1') ORDER BY datname").scalars())
        record = {'captured_at': now(), 'server_version': version, 'server_version_num': number,
                  'databases': databases, 'python': sys.version,
                  'installed': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}}
        save(name + '.json', record)
        if number // 10000 != 16 or databases:
            raise RuntimeError('Exact PostgreSQL 16 and empty disposable service required')
    finally:
        engine.dispose()


def tests():
    sys.path.insert(0, str(Path.cwd()))
    from backend.tests import test_postgres as fixtures
    events, databases = [], []
    original_database = fixtures.PostgreSQLTests.database
    active = [None]

    @contextmanager
    def observed_database(self, profile=None):
        entry = {'test_id': active[0], 'profile': profile, 'entered_at': now(),
                 'database': None, 'fixture_cleanup_completed': False}
        databases.append(entry)
        try:
            with original_database(self, profile) as engine:
                entry['database'] = engine.url.database
                yield engine
            entry['fixture_cleanup_completed'] = True
        finally:
            entry['finished_at'] = now()

    fixtures.PostgreSQLTests.database = observed_database
    # Remediation aliases the fixture at import time, before the owner gate loads it.
    original_runner = unittest.TextTestRunner

    class Result(unittest.TextTestResult):
        def startTest(self, test):
            active[0] = test.id()
            events.append({'id': test.id(), 'started_at': now(), 'status': 'RUNNING', 'subtests': []})
            super().startTest(test)

        def stopTest(self, test):
            events[-1]['finished_at'] = now()
            active[0] = None
            super().stopTest(test)

        def addSuccess(self, test):
            events[-1]['status'] = 'PASS'
            super().addSuccess(test)

        def addFailure(self, test, err):
            events[-1]['status'] = 'FAIL'
            super().addFailure(test, err)

        def addError(self, test, err):
            # setUpClass errors have no preceding startTest.
            if events and events[-1]['id'] == test.id():
                events[-1]['status'] = 'ERROR'
            else:
                events.append({'id': test.id(), 'status': 'ERROR', 'subtests': []})
            super().addError(test, err)

        def addSkip(self, test, reason):
            events[-1].update(status='SKIP', reason=reason)
            super().addSkip(test, reason)

        def addExpectedFailure(self, test, err):
            events[-1]['status'] = 'EXPECTED_FAILURE'
            super().addExpectedFailure(test, err)

        def addUnexpectedSuccess(self, test):
            events[-1]['status'] = 'UNEXPECTED_SUCCESS'
            super().addUnexpectedSuccess(test)

        def addSubTest(self, test, subtest, err):
            events[-1]['subtests'].append({'id': subtest.id(), 'status': 'PASS' if err is None else 'FAIL'})
            super().addSubTest(test, subtest, err)

    class Runner(original_runner):
        resultclass = Result

    unittest.TextTestRunner = Runner
    try:
        runpy.run_path(str(Path('docs/acceptance/MS7-MIG-V01/run-target-ci-v5.py').resolve()), run_name='__main__')
    finally:
        unittest.TextTestRunner = original_runner
        fixtures.PostgreSQLTests.database = original_database
        save('test-observations.json', {'tests': events, 'databases': databases})


if __name__ == '__main__':
    if sys.argv[1] in ('postgres-before', 'postgres-after'):
        probe(sys.argv[1])
    elif sys.argv[1] == 'tests':
        tests()
    else:
        raise SystemExit('Unknown observer action')
