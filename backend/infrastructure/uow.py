"""One session per operation. Explicit commit; default exit is rollback."""
from sqlalchemy.exc import OperationalError, InterfaceError
from sqlalchemy.orm import sessionmaker
from .database import DatabaseUnavailable
from .repositories import Repository


class UnitOfWork:
    def __init__(self, engine):
        self._factory = sessionmaker(engine, expire_on_commit=False, autoflush=False)
        self.session = None

    def __enter__(self):
        if self.session is not None:
            raise RuntimeError('Unit of work is already active')
        self.session = self._factory()
        self.session.begin()
        return self

    def repository(self, model):
        if self.session is None:
            raise RuntimeError('Unit of work is inactive')
        return Repository(self.session, model)

    def commit(self):
        try:
            self.session.commit()
        except (OperationalError, InterfaceError):
            self.session.rollback()
            raise DatabaseUnavailable('Database operation unavailable; outcome requires reconciliation') from None

    def __exit__(self, exc_type, exc, traceback):
        try:
            self.session.rollback()
        finally:
            self.session.close()
            self.session = None
        if isinstance(exc, (OperationalError, InterfaceError)):
            raise DatabaseUnavailable('Database operation unavailable; outcome requires reconciliation') from None
