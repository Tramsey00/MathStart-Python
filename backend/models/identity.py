"""MS-T009 additive Identity storage; historical tables are unchanged."""
import sqlalchemy as sa
from backend.models.baseline import metadata

account = sa.Table('identity_recovery_address', metadata,
    sa.Column('user_id', sa.Integer, sa.ForeignKey('auth_user.id', ondelete='CASCADE'), primary_key=True),
    sa.Column('email', sa.String(254)),
    sa.Column('verified_email', sa.String(254), unique=True),
    sa.Column('verified_at', sa.DateTime(timezone=True)))
token = sa.Table('identity_action_token', metadata,
    sa.Column('digest', sa.String(64), primary_key=True),
    sa.Column('user_id', sa.Integer, sa.ForeignKey('auth_user.id', ondelete='CASCADE'), nullable=False, index=True),
    sa.Column('purpose', sa.String(12), nullable=False),
    sa.Column('email', sa.String(254), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, index=True),
    sa.CheckConstraint("purpose IN ('verify','reset')", name='identity_token_purpose'))
window = sa.Table('identity_request_window', metadata,
    sa.Column('key', sa.String(64), primary_key=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, index=True),
    sa.Column('count', sa.Integer, nullable=False),
    sa.CheckConstraint('count >= 0', name='identity_window_count'))
event = sa.Table('identity_security_event', metadata,
    sa.Column('id', sa.Uuid, primary_key=True),
    sa.Column('kind', sa.String(32), nullable=False),
    sa.Column('subject', sa.String(64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, index=True))
IDENTITY_TABLES = [account, token, window, event]
