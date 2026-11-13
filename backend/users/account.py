"""Account actions extend existing Identity, session and receipt authority."""
from datetime import timedelta
import hashlib
import math
import secrets
import uuid
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from backend.infrastructure.uow import UnitOfWork
from backend.infrastructure.http import transport as wire
from backend.infrastructure.locks import OrderedLocks
from backend.models.baseline import User
from backend.models.identity import account, token, window, event
from backend.users import passwords
from backend.users.security import salted_hmac, revoke_user
from backend.users.service import validate_current

def token_digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

class AccountService:
    def __init__(self, identity, mail):
        self.identity, self.security, self.engine, self.mail = identity, identity.security, identity.engine, mail

    def budget(self, action, remote, login=''):
        # Shared PG row locks; every admitted attempt (including success) counts.
        policies = {'login': [(f'ip:{remote}', 300, 300), (f'pair:{remote}:{login}', 10, 300), (f'login:{login}', 100, 300)],
                    'register': [(f'ip:{remote}', 30, 3600)],
                    'recover': [(f'ip:{remote}', 60, 3600), (f'login:{login}', 5, 900)],
                    'sensitive': [(f'ip:{remote}', 60, 900), (f'owner:{login}', 10, 900)],
                    'consume': [(f'ip:{remote}', 60, 900)]}
        retry = 0
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            self.security.writer(s)
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            for subject, maximum, seconds in sorted(policies[action]):
                key = salted_hmac('identity.budget.' + action, subject, self.security.key)
                s.execute(insert(window).values(key=key, started_at=now, count=0).on_conflict_do_nothing())
                row = s.execute(sa.select(window).where(window.c.key == key).with_for_update()).mappings().one()
                elapsed = (now - row['started_at']).total_seconds()
                count = row['count'] if elapsed < seconds else 0
                if count >= maximum:
                    retry = max(retry, math.ceil(seconds - elapsed), 1)
                else:
                    s.execute(window.update().where(window.c.key == key).values(count=count + 1,
                        started_at=row['started_at'] if elapsed < seconds else now))
            s.execute(window.delete().where(window.c.started_at < now - timedelta(days=2)))
            s.execute(event.delete().where(event.c.created_at < now - timedelta(days=30)))
            s.execute(token.delete().where(token.c.expires_at < now))
            if retry:
                self.audit(s, 'rate_limited', action + ':' + remote, now)
            uow.commit()
        if retry:
            error = wire.APIError(429, 'RATE_LIMITED', 'Try again later.')
            error.retry_after = retry
            raise error

    def audit(self, s, kind, subject, now):
        s.execute(event.insert().values(id=uuid.uuid4(), kind=kind,
            subject=salted_hmac('identity.audit', str(subject), self.security.key), created_at=now))

    def record(self, kind, subject):
        with UnitOfWork(self.engine) as uow:
            self.security.writer(uow.session)
            self.audit(uow.session, kind, subject, uow.session.scalar(sa.select(sa.func.clock_timestamp())))
            uow.commit()

    def state(self, identity):
        with UnitOfWork(self.engine) as uow:
            user = uow.session.get(User, identity.user_id)
            validate_current(uow.session, identity, user, self.security.keys, lock=False)
            row = uow.session.execute(sa.select(account).where(account.c.user_id == user.id)).mappings().first()
            return {'email': row['email'] if row else None,
                    'email_verified': bool(row and row['verified_email'] and row['verified_email'] == row['email']),
                    'mail_available': self.mail.available}

    def _owner(self, s, identity, current_password):
        OrderedLocks(s).namespace('identity', 'lineage:' + str(identity.lineage_id))
        user = s.scalar(sa.select(User).where(User.id == identity.user_id).with_for_update())
        validate_current(s, identity, user, self.security.keys, lock=False)
        if not passwords.verify(current_password, user.password):
            raise wire.authentication_required()
        return user

    def _issue(self, s, user, purpose, email, now):
        raw = secrets.token_urlsafe(32)
        s.execute(token.delete().where(token.c.user_id == user.id, token.c.purpose == purpose))
        s.execute(token.insert().values(digest=token_digest(raw), user_id=user.id, purpose=purpose, email=email,
            expires_at=now + timedelta(minutes=30 if purpose == 'reset' else 60)))
        # Fragment is never sent in an HTTP request, access log or Referer.
        return self.security.origin + '/auth?mode=' + purpose + '#token=' + raw

    def action(self, identity, action, body):
        delivery = None
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            self.security.writer(s)
            user = self._owner(s, identity, body['current_password'])
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            if action == 'password':
                if not passwords.validate_new_password(body['new_password'], user):
                    raise wire.invalid()
                user.password = passwords.encode(body['new_password'])
                revoke_user(s, user.id, now)
                s.execute(token.delete().where(token.c.user_id == user.id))
            elif action == 'sessions':
                revoke_user(s, user.id, now)
            elif action == 'email':
                address = body['email'].strip().lower()
                if address and (not passwords.valid_email(address) or not address.isascii()):
                    raise wire.invalid()
                if address and not self.mail.available:
                    raise wire.unavailable()
                # An unconfirmed address never reserves a unique address.
                s.execute(token.delete().where(token.c.user_id == user.id))
                s.execute(insert(account).values(user_id=user.id).on_conflict_do_nothing())
                s.execute(account.update().where(account.c.user_id == user.id).values(
                    email=address or None, verified_email=None, verified_at=None))
                if address:
                    delivery = (address, 'verify', self._issue(s, user, 'verify', address, now))
            self.audit(s, action, user.id, now)
            uow.commit()
        if delivery:
            self._deliver(*delivery)
        return {'completed': True}

    def _deliver(self, *message):
        try:
            self.mail.send(*message)
        except Exception:
            # Never expose provider exception text or token/address.
            raise wire.unavailable() from None

    def _recover_deliver(self, message):
        try:
            self.mail.send(*message)
        except Exception:
            self.record('recovery_delivery_failed', message[0])

    def recover(self, username, *, defer=None):
        if not self.mail.available:
            raise wire.unavailable()  # same response for every account
        delivery = None
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            self.security.writer(s)
            user = s.scalar(sa.select(User).where(User.username == username).with_for_update())
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            if user and user.is_active:
                row = s.execute(sa.select(account).where(account.c.user_id == user.id)).mappings().first()
                if row and row['verified_email']:
                    address = row['verified_email']
                    delivery = (address, 'reset', self._issue(s, user, 'reset', address, now))
            self.audit(s, 'recovery_requested', username, now)
            uow.commit()
        if delivery:
            # HTTP schedules this after its generic response, avoiding provider
            # latency/failure revealing whether an account has verified mail.
            if defer:
                defer(self._recover_deliver, delivery)
            else:
                self._recover_deliver(delivery)
        return {'completed': True}

    def consume(self, purpose, body, identity):
        digest = token_digest(body['token'])
        with UnitOfWork(self.engine) as uow:
            s = uow.session
            self.security.writer(s)
            # Read owner, then lock User before Token, same order as issuance/revocation.
            owner = s.scalar(sa.select(token.c.user_id).where(token.c.digest == digest, token.c.purpose == purpose))
            if owner is None:
                raise wire.invalid()
            user = s.scalar(sa.select(User).where(User.id == owner).with_for_update())
            row = s.execute(sa.select(token).where(token.c.digest == digest, token.c.purpose == purpose).with_for_update()).mappings().first()
            now = s.scalar(sa.select(sa.func.clock_timestamp()))
            if not row or not user.is_active or row['expires_at'] <= now:
                raise wire.invalid()
            address = s.execute(sa.select(account).where(account.c.user_id == owner)).mappings().first()
            if purpose == 'verify':
                if identity is None or identity.user_id != owner:
                    raise wire.forbidden()
                validate_current(s, identity, user, self.security.keys, lock=False)
                if not address or address['email'] != row['email']:
                    raise wire.invalid()
                try:
                    with s.begin_nested():
                        s.execute(account.update().where(account.c.user_id == owner).values(
                            verified_email=row['email'], verified_at=now))
                except IntegrityError:
                    raise wire.APIError(409, 'STATE_CONFLICT', 'Address unavailable.') from None
            else:
                if not address or address['verified_email'] != row['email']:
                    raise wire.invalid()
                if not passwords.validate_new_password(body['new_password'], user):
                    raise wire.invalid()
                user.password = passwords.encode(body['new_password'])
                revoke_user(s, owner, now)
            s.execute(token.delete().where(token.c.user_id == owner if purpose == 'reset' else token.c.digest == digest))
            self.audit(s, purpose, owner, now)
            uow.commit()
        return {'completed': True}
