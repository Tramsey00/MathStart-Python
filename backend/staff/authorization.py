"""V03 verifies sessions; V02 rechecks DB flags and effective permissions."""
from dataclasses import dataclass
import hashlib
import json

import sqlalchemy as sa

from backend.models.baseline import User, metadata
from backend.infrastructure.http.transport import authentication_required, forbidden


@dataclass(frozen=True)
class AuthenticatedIdentity:
    """Created only by the trusted server authentication adapter, never request roles."""
    user_id: int


@dataclass(frozen=True)
class StaffScope:
    user_id: int
    superuser: bool
    permissions: frozenset[str]
    revision: str

    def permits(self, *permissions):
        return self.superuser or any(p in self.permissions for p in permissions)


def authorize(uow, identity, *permissions):
    if type(identity) is not AuthenticatedIdentity or type(identity.user_id) is not int:
        raise authentication_required()
    user = uow.repository(User).get(identity.user_id)
    if user is None or not user.is_active:
        raise authentication_required()
    if not user.is_staff:
        raise forbidden()
    p, ct = metadata.tables['auth_permission'], metadata.tables['django_content_type']
    direct, membership, assigned = (metadata.tables[n] for n in
        ['auth_user_user_permissions', 'auth_user_groups', 'auth_group_permissions'])
    ids = sa.union(sa.select(direct.c.permission_id).where(direct.c.user_id == user.id),
                   sa.select(assigned.c.permission_id).join(membership, membership.c.group_id == assigned.c.group_id)
                   .where(membership.c.user_id == user.id))
    codes = frozenset(f'{app}.{code}' for app, code in uow.session.execute(
        sa.select(ct.c.app_label, p.c.codename).join(ct, p.c.content_type_id == ct.c.id).where(p.c.id.in_(ids))))
    revision = hashlib.sha256(json.dumps([user.is_active, user.is_staff, user.is_superuser, sorted(codes)],
                                        separators=(',', ':')).encode()).hexdigest()
    scope = StaffScope(user.id, user.is_superuser, codes, revision)
    if permissions and not scope.permits(*permissions):
        raise forbidden()
    return scope
