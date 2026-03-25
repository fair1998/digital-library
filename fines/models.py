from django.db import models
from loans.models import LoanItem


class Fine(models.Model):
    """Library fines/penalties associated with loan items."""
    TYPE_CHOICES = [
        ('late_return', 'Late Return'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]

    loan_item = models.ForeignKey(
        LoanItem,
        on_delete=models.CASCADE,
        related_name='fines'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unpaid'
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fines'
        verbose_name = 'Fine'
        verbose_name_plural = 'Fines'
        ordering = ['-created_at']

    def __str__(self):
        return f"Fine #{self.id} - {self.get_type_display()} - ${self.amount}"
