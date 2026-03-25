from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from .models import ReservationBatch, Reservation


class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0
    can_delete = False
    fields = ('book', 'status', 'created_at', 'updated_at')
    readonly_fields = ('book', 'created_at', 'updated_at')
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        # ห้ามเพิ่มหนังสือใหม่ใน reservation batch
        return False


@admin.register(ReservationBatch)
class ReservationBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'expires_at', 'reservation_count', 'created_at', 'updated_at')
    list_filter = ('status', 'expires_at', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [ReservationInline]
    readonly_fields = ('user', 'expires_at', 'created_at', 'updated_at', 'reservation_count')
    actions = ['confirm_reservations', 'cancel_reservations']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Reservation Information', {
            'fields': ('user', 'expires_at', 'reservation_count')
        }),
        ('Admin Actions', {
            'fields': ('status',),
            'description': 'อนุมัติหรือยกเลิกการจองหนังสือ'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # ห้าม admin สร้าง reservation batch ใหม่
        return False
    
    def has_delete_permission(self, request, obj=None):
        # ห้ามลบ reservation batch (ใช้ status cancelled แทน)
        return False
    
    def reservation_count(self, obj):
        return obj.reservations.count()
    reservation_count.short_description = 'Books Reserved'
    
    @admin.action(description='ยืนยันการจอง (Confirm selected reservations)')
    def confirm_reservations(self, request, queryset):
        """Confirm selected reservation batches and update book availability."""
        confirmed_count = 0
        failed_count = 0
        
        for batch in queryset:
            if not batch.can_be_confirmed():
                failed_count += 1
                self.message_user(
                    request,
                    f'Batch #{batch.id} cannot be confirmed (status: {batch.status}, expired: {batch.is_expired()})',
                    level=messages.WARNING
                )
                continue
            
            try:
                with transaction.atomic():
                    # Check availability for all items first
                    for reservation in batch.reservations.all():
                        if reservation.book.available_quantity <= 0:
                            raise ValueError(f'Book "{reservation.book.title}" is not available')
                    
                    # Update batch status
                    batch.status = 'confirmed'
                    batch.save()
                    
                    # Update each reservation and decrease book quantity
                    for reservation in batch.reservations.all():
                        reservation.status = 'confirmed'
                        reservation.save()
                        
                        # Decrease available quantity
                        book = reservation.book
                        book.available_quantity -= 1
                        book.save()
                    
                    confirmed_count += 1
                    
            except Exception as e:
                failed_count += 1
                self.message_user(
                    request,
                    f'Error confirming Batch #{batch.id}: {str(e)}',
                    level=messages.ERROR
                )
        
        if confirmed_count > 0:
            self.message_user(
                request,
                f'Successfully confirmed {confirmed_count} reservation batch(es)',
                level=messages.SUCCESS
            )
        
        if failed_count > 0:
            self.message_user(
                request,
                f'Failed to confirm {failed_count} reservation batch(es)',
                level=messages.WARNING
            )
    
    @admin.action(description='ยกเลิกการจอง (Cancel selected reservations)')
    def cancel_reservations(self, request, queryset):
        """Cancel selected reservation batches and restore book availability if needed."""
        cancelled_count = 0
        failed_count = 0
        
        for batch in queryset:
            if not batch.can_be_cancelled():
                failed_count += 1
                self.message_user(
                    request,
                    f'Batch #{batch.id} cannot be cancelled (status: {batch.status})',
                    level=messages.WARNING
                )
                continue
            
            try:
                with transaction.atomic():
                    # Store old status to check if we need to restore quantities
                    old_status = batch.status
                    
                    # Update batch status
                    batch.status = 'cancelled'
                    batch.save()
                    
                    # Update each reservation and restore book quantity if it was confirmed
                    for reservation in batch.reservations.all():
                        # If reservation was confirmed, we need to restore the quantity
                        if reservation.status == 'confirmed':
                            book = reservation.book
                            book.available_quantity += 1
                            book.save()
                        
                        reservation.status = 'cancelled'
                        reservation.save()
                    
                    cancelled_count += 1
                    
            except Exception as e:
                failed_count += 1
                self.message_user(
                    request,
                    f'Error cancelling Batch #{batch.id}: {str(e)}',
                    level=messages.ERROR
                )
        
        if cancelled_count > 0:
            self.message_user(
                request,
                f'Successfully cancelled {cancelled_count} reservation batch(es)',
                level=messages.SUCCESS
            )
        
        if failed_count > 0:
            self.message_user(
                request,
                f'Failed to cancel {failed_count} reservation batch(es)',
                level=messages.WARNING
            )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'reservation_batch_id', 'batch_user', 'batch_status', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'reservation_batch__status')
    search_fields = ('id', 'book__title', 'book__id', 'reservation_batch__user__username', 'reservation_batch__user__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_select_related = ('book', 'reservation_batch', 'reservation_batch__user')
    autocomplete_fields = ['book', 'reservation_batch']
    list_per_page = 20
    readonly_fields = ('reservation_batch', 'book', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Reservation Details', {
            'fields': ('reservation_batch', 'book')
        }),
        ('Admin Actions', {
            'fields': ('status',),
            'description': 'อนุมัติหรือยกเลิกการจองหนังสือแต่ละเล่ม'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # ห้าม admin สร้าง reservation ใหม่
        return False
    
    def has_delete_permission(self, request, obj=None):
        # ห้ามลบ reservation (ใช้ status cancelled แทน)
        return False
    
    def batch_user(self, obj):
        return obj.reservation_batch.user.username
    batch_user.short_description = 'User'
    batch_user.admin_order_field = 'reservation_batch__user__username'
    
    def batch_status(self, obj):
        return obj.reservation_batch.status
    batch_status.short_description = 'Batch Status'
    batch_status.admin_order_field = 'reservation_batch__status'
    
    def reservation_batch_id(self, obj):
        return f"#{obj.reservation_batch.id}"
    reservation_batch_id.short_description = 'Batch'
    reservation_batch_id.admin_order_field = 'reservation_batch__id'
