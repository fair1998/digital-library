from django.db import models
from django.conf import settings
from books.models import Book
from reservations.models import Reservation


class LoanBatch(models.Model):
    """Header/parent record for a single borrowing transaction."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_batches'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loan_batches'
        verbose_name = 'Loan Batch'
        verbose_name_plural = 'Loan Batches'
        ordering = ['-created_at']

    def __str__(self):
        return f"Loan Batch #{self.id} - {self.user.username}"


class LoanItem(models.Model):
    """Individual borrowed books within a loan batch."""
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='loan_items'
    )
    loan_batch = models.ForeignKey(
        LoanBatch,
        on_delete=models.CASCADE,
        related_name='loan_items'
    )
    reservation = models.OneToOneField(
        Reservation,
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
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'loan_items'
        verbose_name = 'Loan Item'
        verbose_name_plural = 'Loan Items'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.book.title} - {self.get_status_display()}"
