from django.db import models
from django.conf import settings
from django.utils import timezone
from books.models import Book
from typing import TYPE_CHECKING
from django.db.models import Manager

if TYPE_CHECKING:
    from holds.models import HoldItem

class Hold(models.Model):
    """Header/parent record for a single hold transaction."""
    
    STATUS_CHOICES = [
        ('pending', 'รอการยืนยัน'),
        ('confirmed', 'ยืนยันแล้ว - รอรับหนังสือ'),
        ('completed', 'เสร็จสิ้น'),
        ('expired', 'หมดอายุ'),
        ('cancelled', 'ยกเลิก'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='holds')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Expiry time for confirmed hold - user must pick up books before this time')
    created_at = models.DateTimeField(auto_now_add=True)

    if TYPE_CHECKING:
        hold_items: Manager[HoldItem]
    
    class Meta:
        db_table = 'holds'
        verbose_name = 'Hold'
        verbose_name_plural = 'Holds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Hold #{self.id} - {self.user.username} ({self.status})"
    
    @property
    def status_label(self) -> str:
        return self.get_status_display() # type: ignore[attr-defined]
    
    @property
    def is_expired(self):
        """Check if hold has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def can_be_confirmed(self):
        """Check if hold can be confirmed by admin."""
        if self.status != 'pending':
            return False
        # No expiry check here since admin sets expiry when confirming
        # Check if all items in the hold can be confirmed
        for item in self.hold_items.all():
            if not item.can_be_confirmed:
                return False
        return True

    @property    
    def can_be_cancelled(self):
        """Check if hold can be cancelled by admin."""
        # Can cancel if pending or confirmed (but not yet converted to loan)
        return self.status in ['pending', 'confirmed']
    
    @property       
    def can_be_cancelled_by_user(self):
        """Check if user can cancel this hold."""
        # User can only cancel pending holds
        return self.status == 'pending'


class HoldItem(models.Model):
    """Individual reserved books within a hold."""
    
    STATUS_CHOICES = [
        ('pending', 'รอการยืนยัน'),
        ('confirmed', 'ยืนยันแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]
    
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='hold_items')
    hold = models.ForeignKey(Hold, on_delete=models.CASCADE, related_name='hold_items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hold_items'
        verbose_name = 'Hold Item'
        verbose_name_plural = 'Hold Items'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.book.title} - Hold #{self.hold.id} ({self.status})"

    @property
    def can_be_confirmed(self):
        """Check if this hold item can be confirmed."""
        if self.status != 'pending':
            return False
        # Check if book is available
        if self.book.available_quantity <= 0:
            return False
        return True

    @property    
    def can_be_cancelled(self):
        """Check if this hold item can be cancelled."""
        return self.status in ['pending', 'confirmed']
