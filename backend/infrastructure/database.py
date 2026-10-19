"""Explicit backend selection. Never log URLs or underlying DBAPI messages."""
from dataclasses import dataclass
import os

import sqlalchemy as sa
from sqlalchemy.engine import URL, make_url


class DatabaseUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class DatabaseConfig:
    url: URL
    sqlite_compatibility: bool = False

    @classmethod
    def from_environment(cls):
        backend = os.environ.get('MATHSTART_DB_BACKEND', 'postgresql')
        if backend == 'sqlite':
            path = os.environ.get('MATHSTART_SQLITE_PATH')
            if not path:
                raise ValueError('Explicit SQLite path is required')
            return cls(URL.create('sqlite+pysqlite', database=path), True)
        if backend != 'postgresql':
            raise ValueError('Unsupported database backend')
        raw = os.environ.get('MATHSTART_DATABASE_URL')
        if not raw:
            raise ValueError('Explicit PostgreSQL configuration is required')
        try:
            url = make_url(raw)
        except Exception:
            raise ValueError('Invalid database configuration') from None
        if url.drivername != 'postgresql+psycopg':
            raise ValueError('PostgreSQL psycopg driver is required')
        return cls(url)


def create_engine(config):
    if config.url.drivername.startswith('sqlite'):
        if not config.sqlite_compatibility:
            raise ValueError('SQLite compatibility must be explicitly selected')
        engine = sa.create_engine(config.url, echo=False)
        @sa.event.listens_for(engine, 'connect')
        def foreign_keys(dbapi_connection, _):
            dbapi_connection.execute('PRAGMA foreign_keys=ON')
        return engine
    if config.url.drivername != 'postgresql+psycopg':
        raise ValueError('Unsupported database driver')
    return sa.create_engine(config.url, echo=False, hide_parameters=True, pool_pre_ping=True,
                            connect_args={'connect_timeout': 5, 'options': '-c statement_timeout=30000 -c lock_timeout=5000'})


def check_connection(engine):
    try:
        with engine.connect() as connection:
            connection.execute(sa.text('SELECT 1'))
    except sa.exc.DBAPIError:
        raise DatabaseUnavailable('Database connection unavailable') from None
