from django.db import models
from django.conf import settings
from books.models import Book


class ReservationBatch(models.Model):
    """Header/parent record for a single reservation transaction."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservation_batches')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reservation_batches'
        verbose_name = 'Reservation Batch'
        verbose_name_plural = 'Reservation Batches'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reservation #{self.id} - {self.user.username} ({self.status})"


class Reservation(models.Model):
    """Individual reserved books within a reservation batch."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reservation_batch = models.ForeignKey(ReservationBatch, on_delete=models.CASCADE, related_name='reservations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reservations'
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.book.title} - Batch #{self.reservation_batch.id} ({self.status})"
