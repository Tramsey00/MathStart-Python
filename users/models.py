import uuid

from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    class OnboardingMode(models.TextChoices):
        START_ZERO = "START_ZERO"
        DIAGNOSTIC = "DIAGNOSTIC"
        SELF_REPORT = "SELF_REPORT"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    selected_grade = models.ForeignKey(
        "content.Grade", null=True, blank=True, on_delete=models.PROTECT,
    )
    onboarding_mode = models.CharField(
        max_length=16, choices=OnboardingMode.choices, null=True, blank=True,
    )
    onboarding_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(onboarding_complete=False, onboarding_mode__isnull=True)
                    | models.Q(
                        onboarding_complete=True,
                        onboarding_mode__in=["START_ZERO", "DIAGNOSTIC", "SELF_REPORT"],
                        onboarding_mode__isnull=False,
                        selected_grade__isnull=False,
                    )
                ),
                name="users_consistent_onboarding",
            ),
        ]


class IdentityReceipt(models.Model):
    """Private replay record. Never stores credentials or raw request bodies."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scope = models.CharField(max_length=80)
    operation = models.CharField(max_length=32)
    key_digest = models.CharField(max_length=64)
    request_digest = models.CharField(max_length=64)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)
    response = models.JSONField(null=True)
    status = models.PositiveSmallIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["scope", "operation", "key_digest"],
                name="users_unique_identity_receipt",
            ),
            models.CheckConstraint(
                condition=(models.Q(status__isnull=True, response__isnull=True)
                           | models.Q(status__isnull=False, response__isnull=False,
                                      user__isnull=False)),
                name="users_consistent_receipt",
            ),
        ]


class LoginWindow(models.Model):
    """Shared fixed-window login counter; keyed by a private IP HMAC."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_digest = models.CharField(max_length=64, unique=True)
    started_at = models.DateTimeField()
    count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(count__lte=10), name="users_login_limit"),
        ]
