from alembic import context
from backend.models.baseline import metadata
import backend.models.protocol
from backend.infrastructure.database import DatabaseConfig, create_engine

config = context.config
if not config.attributes.get('v01_checked'):
    raise RuntimeError('Use the guarded V01 adapter; direct Alembic upgrade/stamp is forbidden')
if context.is_offline_mode():
    raise RuntimeError('Offline stamping/upgrades are forbidden: schema inspection is required')


def run(connection):
    context.configure(connection=connection, target_metadata=metadata,
                      compare_type=True, compare_server_default=True,
                      transaction_per_migration=False)
    with context.begin_transaction():
        context.run_migrations()


connection = config.attributes.get('connection')
if connection is not None:
    run(connection)
else:
    engine = create_engine(DatabaseConfig.from_environment())
    try:
        with engine.begin() as connection:
            run(connection)
    finally:
        engine.dispose()
