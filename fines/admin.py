from django.contrib import admin
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
        'paid_at'
    ]
    list_filter = ['type', 'paid_at']
    search_fields = [
        'id',
        'loan_item__book__title',
        'loan_item__loan__user__username',
        'loan_item__loan__user__email',
        'loan_item__loan__user__first_name',
        'loan_item__loan__user__last_name',
        'reason'
    ]
    readonly_fields = ['paid_at']
    list_select_related = ['loan_item', 'loan_item__book', 'loan_item__loan_batch', 'loan_item__loan__user']
    autocomplete_fields = ['loan_item']
    
    fieldsets = (
        ('Fine Information', {
            'fields': ('loan_item', 'type', 'amount', 'reason')
        }),
        ('Payment Information', {
            'fields': ('paid_at',)
        }),
    )
    
    date_hierarchy = 'paid_at'
    
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
        user = obj.loan_item.loan.user
        return f"{user.get_full_name() or user.username}"
    borrower_name.short_description = 'Borrower'
    borrower_name.admin_order_field = 'loan_item__loan__user__username'
    
    def amount_display(self, obj):
        """Display amount with currency symbol."""
        return f"{obj.amount} บาท"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
