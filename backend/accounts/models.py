from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Adult account holder; children will never be login accounts."""

    email_verified = models.BooleanField(default=False)

    class Meta(AbstractUser.Meta):
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("email"),
                condition=~models.Q(email=""),
                name="unique_account_email",
            )
        ]
