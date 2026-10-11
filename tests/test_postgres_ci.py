"""Reject incomplete, stale or unowned V01 CI evidence at the R03 boundary."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import postgres_ci as ci

CONFIG = json.loads(ci.CONFIG.read_text())


def fixture():
    unit = ['backend.tests.test_unit.UnitTests.test_' + str(i) for i in range(11)]
    postgres = ['backend.tests.test_postgres.PostgreSQLTests.test_' + str(i) for i in range(21)]
    postgres += ['backend.tests.test_postgres.PostgreSQLTests.test_fresh_twice_separate_databases_no_django',
                 'backend.tests.test_postgres.PostgreSQLTests.test_upgrade_profiles_preserve_data_defaults_epoch_sequences']
    manifest = {'cases': [{'id': name, 'environment': 'unit' if name in unit else 'PostgreSQL'} for name in unit + postgres]}
    observed = {'tests': [{'id': name, 'status': 'PASS', 'subtests': []} for name in unit + postgres],
                'databases': [{'test_id': postgres[-2 if i < 2 else -1], 'profile': None if i < 2 else 'ABC'[i-2],
                               'database': 'test_ms7_mig_v01_' + format(i, '032x'),
                               'fixture_cleanup_completed': True} for i in range(5)]}
    return observed, manifest


class PostgreSQLEvidenceTests(unittest.TestCase):
    def test_complete_evidence_requires_actual_fresh_and_profiles(self):
        observed, manifest = fixture()
        result = ci.validate_observations(observed, manifest)
        self.assertEqual((result['target_tests_passed'], result['postgres_tests_passed']), (34, 23))
        self.assertEqual(result['upgrade_profiles'], ['A', 'B', 'C'])

    def test_missing_duplicate_unknown_case_rejected(self):
        for mutation in ('missing', 'duplicate', 'unknown'):
            observed, manifest = fixture()
            if mutation == 'missing': observed['tests'].pop()
            elif mutation == 'duplicate': observed['tests'][0] = copy.deepcopy(observed['tests'][1])
            else: observed['tests'][0]['id'] = 'unexpected'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                ci.validate_observations(observed, manifest)

    def test_skipped_failed_error_expected_failure_and_subtest_rejected(self):
        for state in ('SKIP', 'FAIL', 'ERROR', 'EXPECTED_FAILURE', 'UNEXPECTED_SUCCESS', 'RUNNING'):
            observed, manifest = fixture(); observed['tests'][0]['status'] = state
            with self.subTest(state=state), self.assertRaises(ValueError):
                ci.validate_observations(observed, manifest)
        observed, manifest = fixture(); observed['tests'][0]['subtests'] = [{'status': 'FAIL'}]
        with self.assertRaises(ValueError): ci.validate_observations(observed, manifest)

    def test_twenty_three_postgres_cases_required(self):
        observed, manifest = fixture(); manifest['cases'][0]['environment'] = 'PostgreSQL'
        with self.assertRaises(ValueError): ci.validate_observations(observed, manifest)

    def test_fresh_repeat_or_upgrade_profile_missing_rejected(self):
        for index in (0, 2, 3, 4):
            observed, manifest = fixture(); observed['databases'].pop(index)
            with self.subTest(index=index), self.assertRaises(ValueError):
                ci.validate_observations(observed, manifest)
        observed, manifest = fixture(); observed['databases'][2]['profile'] = 'C'
        with self.assertRaises(ValueError): ci.validate_observations(observed, manifest)

    def test_foreign_reused_or_uncleaned_database_rejected(self):
        for key, value in (('database', 'shared-production'), ('database', 'test_ms7_mig_v01_' + '1'*32),
                           ('fixture_cleanup_completed', False)):
            observed, manifest = fixture()
            if key == 'database' and value.startswith('test_'): value = observed['databases'][1]['database']
            observed['databases'][0][key] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                ci.validate_observations(observed, manifest)

    def test_changed_live_head_base_or_actual_checkout_rejected(self):
        pr = {'number': 51, 'state': 'open', 'head': {'sha': CONFIG['pr_head_sha'], 'repo': {'full_name': CONFIG['repository']}},
              'base': {'sha': CONFIG['pr_base_sha'], 'repo': {'full_name': CONFIG['repository']}}}
        ci.check_identity(CONFIG, pr, CONFIG['pr_head_sha'])
        for key in ('head', 'base'):
            stale = copy.deepcopy(pr); stale[key]['sha'] = 'stale'
            with self.assertRaises(ValueError): ci.check_identity(CONFIG, stale, CONFIG['pr_head_sha'])
        with self.assertRaises(ValueError): ci.check_identity(CONFIG, pr, 'stale-checkout')

    def test_service_id_image_and_reserved_port_required(self):
        service = {'id': 'a'*64, 'configured_image': 'postgres:16-bookworm',
                   'ports': {'5432/tcp': [{'HostPort': '55441'}]}}
        ci.validate_service(service, 'a'*64)
        for key, value in (('id', 'b'*64), ('configured_image', 'postgres:17'), ('ports', {'5432/tcp': [{'HostPort': '5432'}]})):
            changed = copy.deepcopy(service); changed[key] = value
            with self.assertRaises(ValueError): ci.validate_service(changed, 'a'*64)

    def test_only_exact_twenty_two_locked_packages_allowed(self):
        lock = '\n'.join(f'package-{i}==1.2.3' for i in range(22))
        installed = {f'package_{i}': '1.2.3' for i in range(22)}; installed['pip'] = '25.0.1'
        ci.validate_lock(lock, installed)
        for key, value in (('package_0', 'different'), ('unexpected', '1')):
            changed = dict(installed); changed[key] = value
            with self.assertRaises(ValueError): ci.validate_lock(lock, changed)

    def test_evidence_cannot_overwrite_previous_record(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(ci, 'OUTPUT', Path(directory)):
            ci.save('receipt.json', {'status': 'first'})
            with self.assertRaises(FileExistsError): ci.save('receipt.json', {'status': 'replacement'})
            self.assertEqual(json.loads((Path(directory)/'receipt.json').read_text()), {'status': 'first'})


if __name__ == '__main__':
    unittest.main()
