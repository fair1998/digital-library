from django.contrib import admin
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Hold, HoldItem
from books.models import Book


class HoldItemInline(admin.TabularInline):
    model = HoldItem
    extra = 1
    can_delete = False
    fields = ('book', 'status', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['book']
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return True


@admin.register(Hold)
class HoldAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'expires_at', 'hold_item_count', 'created_at')
    list_filter = ('status', 'expires_at', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [HoldItemInline]
    readonly_fields = ('created_at', 'hold_item_count')
    actions = ['confirm_hold_items', 'cancel_hold_items']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Hold Item Information', {
            'fields': ('user', 'status', 'expires_at', 'hold_item_count')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def hold_item_count(self, obj):
        return obj.hold_items.count()
    hold_item_count.short_description = 'Books Reserved'
    
    @admin.action(description='ยืนยันการจอง (Confirm selected hold items)')
    def confirm_hold_items(self, request, queryset):
        """Confirm selected hold item batches, set expiry date, and update book availability."""
        confirmed_count = 0
        failed_count = 0
        
        # Get expiry days from settings or use default (3 days)
        expiry_days = getattr(settings, 'RESERVATION_EXPIRY_DAYS', 3)
        
        for batch in queryset:
            if not batch.can_be_confirmed():
                failed_count += 1
                self.message_user(
                    request,
                    f'Batch #{batch.id} cannot be confirmed (status: {batch.status})',
                    level=messages.WARNING
                )
                continue
            
            try:
                with transaction.atomic():
                    # Check availability for all items first
                    for hold_item in batch.hold_items.all():
                        if hold_item.book.available_quantity <= 0:
                            raise ValueError(f'Book "{hold_item.book.title}" is not available')
                    
                    # Update batch status and set expiry date
                    batch.status = 'confirmed'
                    batch.expires_at = timezone.now() + timedelta(days=expiry_days)
                    batch.save()
                    
                    # Update each hold item and decrease book quantity
                    for hold_item in batch.hold_items.all():
                        hold_item.status = 'confirmed'
                        hold_item.save()
                        
                        # Decrease available quantity
                        book = hold_item.book
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
                f'Successfully confirmed {confirmed_count} hold item batch(es) with {expiry_days}-day expiry',
                level=messages.SUCCESS
            )
        
        if failed_count > 0:
            self.message_user(
                request,
                f'Failed to confirm {failed_count} hold item batch(es)',
                level=messages.WARNING
            )
    
    @admin.action(description='ยกเลิกการจอง (Cancel selected hold items)')
    def cancel_hold_items(self, request, queryset):
        """Cancel selected hold item batches and restore book availability if needed."""
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
                    
                    # Update each hold item and restore book quantity if it was confirmed
                    for hold_item in batch.hold_items.all():
                        # If hold item was confirmed, we need to restore the quantity
                        if hold_item.status == 'confirmed':
                            book = hold_item.book
                            book.available_quantity += 1
                            book.save()
                        
                        hold_item.status = 'cancelled'
                        hold_item.save()
                    
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
                f'Successfully cancelled {cancelled_count} hold item batch(es)',
                level=messages.SUCCESS
            )
        
        if failed_count > 0:
            self.message_user(
                request,
                f'Failed to cancel {failed_count} hold item batch(es)',
                level=messages.WARNING
            )


@admin.register(HoldItem)
class HoldItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'hold_id', 'batch_user', 'batch_status', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'hold__status')
    search_fields = ('id', 'book__title', 'book__id', 'hold__user__username', 'hold__user__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_select_related = ('book', 'hold', 'hold__user')
    autocomplete_fields = ['book', 'hold']
    list_per_page = 20
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Hold Item Details', {
            'fields': ('hold', 'book', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True
    
    def batch_user(self, obj):
        return obj.hold.user.username
    batch_user.short_description = 'User'
    batch_user.admin_order_field = 'hold__user__username'
    
    def batch_status(self, obj):
        return obj.hold.status
    batch_status.short_description = 'Batch Status'
    batch_status.admin_order_field = 'hold__status'
    
    def hold_id(self, obj):
        return f"#{obj.hold.id}"
    hold_id.short_description = 'Batch'
    hold_id.admin_order_field = 'hold__id'
