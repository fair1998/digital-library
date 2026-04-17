from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    # Keep only genuinely domain-specific data here.
    # Authentication fields (password, is_active, groups, permissions) are inherited.
    phone_number = models.CharField(max_length=10, null=False, blank=False)
    citizen_id = models.CharField(
    max_length=13,
    unique=True,
    null=False,
    blank=False,
    validators=[
        RegexValidator(
            regex=r'^\d{13}$',
            message='Citizen ID must be exactly 13 digits'
        )
    ])

    # override
    # first_name = models.CharField(max_length=150, blank=False)
    # last_name = models.CharField(max_length=150, blank=False)

    def __str__(self) -> str:
        return self.username
    
    def get_current_borrowed_count(self) -> int:
        """Get the number of books currently borrowed by this user."""
        from loans.models import LoanItem
        return LoanItem.objects.filter(
            loan__user=self,
            status='borrowed'
        ).count()
