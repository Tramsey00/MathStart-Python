"""Capture proposed V01 additive catalog for review; only a fresh disposable DB."""
import json
from pathlib import Path
from alembic import command
from backend.models.protocol import PROTOCOL_TABLES
from backend.migrations.schema import inventory
from backend.migrations.upgrade import configuration, require_disposable, HEAD
from backend.tests.test_postgres import PostgreSQLTests


def main():
    path = Path('backend/migrations/protocol-schema-v1.json')
    if path.exists():
        raise RuntimeError('Do not overwrite an existing reviewed snapshot')
    names = {table.name for table in PROTOCOL_TABLES}
    PostgreSQLTests.setUpClass()
    try:
        with PostgreSQLTests().database() as engine:
            with engine.begin() as connection:
                require_disposable(connection)
                # Generate the proposed catalog before its reference exists.
                # Production fresh() must still validate against that reference.
                command.upgrade(configuration(connection), HEAD)
                observed = inventory(connection)
                result = {'version': 'v01-protocol-schema-v1',
                    'status': 'PROPOSED_V01_DDL_REVIEW_PENDING',
                    'source_sha': '8d958aeeb17da46839722441425ccbb5889e2ab7',
                    'PostgreSQL': connection.scalar(__import__('sqlalchemy').text('SHOW server_version')),
                    'tables': sorted(names)}
                for key, table_key in [('columns', 'table_name'), ('constraints', 'table_name'),
                                       ('indexes', 'tablename'), ('identity_columns', 'table_name')]:
                    result[key] = [row for row in observed[key] if row[table_key] in names]
                owned = {row['owned_sequence'].split('.')[1] for row in result['identity_columns']}
                result['sequences'] = [{k: v for k, v in row.items() if k != 'last_value'}
                                       for row in observed['sequences'] if row['sequencename'] in owned]
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Captured {len(names)} proposed additive tables for V01 DDL review')
    finally:
        PostgreSQLTests.tearDownClass()


if __name__ == '__main__':
    main()
