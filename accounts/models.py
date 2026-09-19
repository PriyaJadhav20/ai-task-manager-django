from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends Django's built-in AbstractUser
    with a `role` field used for role-based access control (RBAC).
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
        help_text="Determines what this user is allowed to see/do.",
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
