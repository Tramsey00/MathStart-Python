"""Reproducible PostgreSQL-only CHECK investigation on a new disposable DB."""
from itertools import product
import json
from pathlib import Path
import sqlalchemy as sa
from backend.models.baseline import SNAPSHOT
from backend.tests.test_postgres import PostgreSQLTests

SOURCE_IN_EXPRESSION = (
    '(NOT onboarding_complete AND onboarding_mode IS NULL) OR '
    "(onboarding_complete AND onboarding_mode IN ('START_ZERO','DIAGNOSTIC','SELF_REPORT') "
    'AND onboarding_mode IS NOT NULL AND selected_grade_id IS NOT NULL)'
)


def investigate(connection):
    frozen = next(item['definition'] for item in SNAPSHOT['physical_baseline']['constraints']
                  if item['name'] == 'users_consistent_onboarding')
    expressions = {'reparsed_frozen_deparse': frozen[7:-1], 'original_in_expression': SOURCE_IN_EXPRESSION}
    observed = {}
    for name, expression in expressions.items():
        # Temporary objects exist only in the caller's disposable connection.
        connection.execute(sa.text(f'CREATE TEMP TABLE {name} ('
            'onboarding_complete boolean, onboarding_mode varchar(16), selected_grade_id bigint, '
            f'CONSTRAINT users_consistent_onboarding CHECK ({expression}))'))
        observed[name] = connection.scalar(sa.text('SELECT pg_get_constraintdef(c.oid) FROM pg_constraint c '
            'JOIN pg_class t ON t.oid=c.conrelid WHERE t.relname=:name AND c.conname=:constraint'),
            {'name': name, 'constraint': 'users_consistent_onboarding'})
    mismatches = []
    combinations = list(product([False, True, None], [None, 'START_ZERO', 'DIAGNOSTIC', 'SELF_REPORT', 'OTHER', '', 'start_zero'], [None, 1]))
    for complete, mode, grade in combinations:
        verdicts = []
        for expression in expressions.values():
            verdicts.append(connection.scalar(sa.text(
                'WITH candidate AS (SELECT CAST(:complete AS boolean) onboarding_complete, '
                'CAST(:mode AS varchar(16)) onboarding_mode, CAST(:grade AS bigint) selected_grade_id) '
                f'SELECT ({expression}) IS NOT FALSE FROM candidate'),
                {'complete': complete, 'mode': mode, 'grade': grade}))
        if verdicts[0] != verdicts[1]:
            mismatches.append({'complete': complete, 'mode': mode, 'grade': grade, 'verdicts': verdicts})
    return {'source_sha': '8d958aeeb17da46839722441425ccbb5889e2ab7',
            'PostgreSQL': connection.scalar(sa.text('SHOW server_version')),
            'frozen_catalog_definition': frozen, 'reparsed_catalog_definitions': observed,
            'original_in_matches_frozen_exactly': observed['original_in_expression'] == frozen,
            'frozen_deparse_roundtrip_matches': observed['reparsed_frozen_deparse'] == frozen,
            'truth_table_cases': len(combinations), 'truth_table_mismatches': mismatches,
            'conclusion': 'Investigative evidence only; exact schema comparator remains unchanged.'}


def main():
    PostgreSQLTests.setUpClass()
    try:
        with PostgreSQLTests().database() as engine:
            with engine.begin() as connection:
                result = investigate(connection)
        path = Path('docs/acceptance/MS7-MIG-V01/check-canonicalization-v1.json')
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: result[k] for k in ['PostgreSQL', 'original_in_matches_frozen_exactly',
            'frozen_deparse_roundtrip_matches', 'truth_table_cases', 'truth_table_mismatches']}, indent=2))
        return 0 if result['original_in_matches_frozen_exactly'] and not result['truth_table_mismatches'] else 1
    finally:
        PostgreSQLTests.tearDownClass()


if __name__ == '__main__':
    raise SystemExit(main())
