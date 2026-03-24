from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Keep only genuinely domain-specific data here.
    # Authentication fields (password, is_active, groups, permissions) are inherited.
    phone_number = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self) -> str:
        return self.username
