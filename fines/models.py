from django.db import models
from loans.models import LoanItem


class Fine(models.Model):
    """Library fines/penalties associated with loan items.
    
    All fines are paid immediately when created (no unpaid status).
    The paid_at timestamp serves as both creation and payment time.
    """
    TYPE_CHOICES = [
        ('late_return', 'Late Return'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]

    loan_item = models.ForeignKey(
        LoanItem,
        on_delete=models.CASCADE,
        related_name='fines'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reason = models.TextField(null=True, blank=True)
    paid_at = models.DateTimeField(
        help_text='Timestamp when fine was paid (also serves as creation time)'
    )

    class Meta:
        db_table = 'fines'
        verbose_name = 'Fine'
        verbose_name_plural = 'Fines'
        ordering = ['-paid_at']

    def __str__(self):
        return f"Fine #{self.id} - {self.get_type_display()} - {self.amount} บาท"
