from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Fine


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'loan_item_display',
        'book_title',
        'borrower_name',
        'type',
        'amount_display',
        'status_display',
        'paid_at',
        'created_at'
    ]
    list_filter = ['type', 'status', 'created_at', 'paid_at']
    search_fields = [
        'id',
        'loan_item__book__title',
        'loan_item__loan_batch__user__username',
        'loan_item__loan_batch__user__email',
        'loan_item__loan_batch__user__first_name',
        'loan_item__loan_batch__user__last_name',
        'reason'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['loan_item', 'loan_item__book', 'loan_item__loan_batch', 'loan_item__loan_batch__user']
    autocomplete_fields = ['loan_item']
    actions = ['mark_as_paid', 'mark_as_unpaid']
    
    fieldsets = (
        ('Fine Information', {
            'fields': ('loan_item', 'type', 'amount', 'reason')
        }),
        ('Payment Status', {
            'fields': ('status', 'paid_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['loan_item']
        return self.readonly_fields
    
    def loan_item_display(self, obj):
        """Display loan item ID with link."""
        return f"Loan Item #{obj.loan_item.id}"
    loan_item_display.short_description = 'Loan Item'
    loan_item_display.admin_order_field = 'loan_item'
    
    def book_title(self, obj):
        """Display book title."""
        return obj.loan_item.book.title
    book_title.short_description = 'Book'
    book_title.admin_order_field = 'loan_item__book__title'
    
    def borrower_name(self, obj):
        """Display borrower's name."""
        user = obj.loan_item.loan_batch.user
        return f"{user.get_full_name() or user.username}"
    borrower_name.short_description = 'Borrower'
    borrower_name.admin_order_field = 'loan_item__loan_batch__user__username'
    
    def amount_display(self, obj):
        """Display amount with currency symbol."""
        return f"${obj.amount}"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_display(self, obj):
        """Display status with colored badge."""
        if obj.status == 'paid':
            color = 'green'
        else:
            color = 'red'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    @admin.action(description='Mark selected fines as paid')
    def mark_as_paid(self, request, queryset):
        """Admin action to mark fines as paid."""
        success_count = 0
        failed_count = 0
        
        for fine in queryset:
            try:
                if fine.status == 'paid':
                    self.message_user(
                        request,
                        f"Fine #{fine.id} is already paid.",
                        level='warning'
                    )
                    failed_count += 1
                    continue
                
                # Mark as paid
                fine.status = 'paid'
                fine.paid_at = timezone.now()
                fine.save()
                success_count += 1
                
            except Exception as e:
                self.message_user(
                    request,
                    f"Error marking Fine #{fine.id} as paid: {str(e)}",
                    level='error'
                )
                failed_count += 1
        
        # Summary message
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully marked {success_count} fine(s) as paid.",
                level='success'
            )
        if failed_count > 0:
            self.message_user(
                request,
                f"Failed to mark {failed_count} fine(s) as paid.",
                level='warning'
            )
    
    @admin.action(description='Mark selected fines as unpaid')
    def mark_as_unpaid(self, request, queryset):
        """Admin action to mark fines as unpaid."""
        success_count = 0
        failed_count = 0
        
        for fine in queryset:
            try:
                if fine.status == 'unpaid':
                    self.message_user(
                        request,
                        f"Fine #{fine.id} is already unpaid.",
                        level='warning'
                    )
                    failed_count += 1
                    continue
                
                # Mark as unpaid
                fine.status = 'unpaid'
                fine.paid_at = None
                fine.save()
                success_count += 1
                
            except Exception as e:
                self.message_user(
                    request,
                    f"Error marking Fine #{fine.id} as unpaid: {str(e)}",
                    level='error'
                )
                failed_count += 1
        
        # Summary message
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully marked {success_count} fine(s) as unpaid.",
                level='success'
            )
        if failed_count > 0:
            self.message_user(
                request,
                f"Failed to mark {failed_count} fine(s) as unpaid.",
                level='warning'
            )
