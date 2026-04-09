from typing import TYPE_CHECKING

from django.db import models
from django.conf import settings
from regex import T
from books.models import Book
from holds.models import HoldItem
from django.utils import timezone
from django.db.models import Manager

class Loan(models.Model):
    """Header/parent record for a single borrowing transaction."""
    STATUS_CHOICES = [
        ('active', 'กำลังยืม'),
        ('completed', 'คืนครบแล้ว'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    if TYPE_CHECKING:
        loan_items: Manager["LoanItem"]

    class Meta:
        db_table = 'loans'
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
        ordering = ['-created_at']

    def __str__(self):
        return f"Loan #{self.id} - {self.user.username}"
    
    @property
    def status_label(self) -> str:
        return self.get_status_display() # type: ignore[attr-defined]

    @property
    def is_overdue(self) -> bool:
        """Check if this loan is overdue."""
        if self.status != 'active' or not self.due_date:
            return False
        return self.due_date < timezone.now()

class LoanItem(models.Model):
    """Individual borrowed books within a loan."""
    STATUS_CHOICES = [
        ('borrowed', 'กำลังยืม'),
        ('returned', 'คืนแล้ว'),
        ('lost', 'หาย'),
    ]

    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='loan_items'
    )
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='loan_items'
    )
    hold_item = models.OneToOneField(
        HoldItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loan_item'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='borrowed'
    )
    returned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loan_items'
        verbose_name = 'Loan Item'
        verbose_name_plural = 'Loan Items'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.book.title}"
    
    @property
    def is_overdue(self) -> bool:
        """Check if this loan item is overdue."""
        if self.status != 'borrowed':
            return False
        return self.loan.is_overdue