from django.contrib import admin
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from .models import LoanBatch, LoanItem


class LoanItemInline(admin.TabularInline):
    model = LoanItem
    extra = 1
    fields = ('book', 'reservation', 'status', 'returned_at')
    autocomplete_fields = ['book', 'reservation']
    readonly_fields = ('returned_at',)


@admin.register(LoanBatch)
class LoanBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'due_date', 'items_count', 'borrowed_count', 'returned_count', 'lost_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'due_date', 'updated_at')
    search_fields = ('id', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    autocomplete_fields = ['user']
    inlines = [LoanItemInline]
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('user', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def items_count(self, obj):
        return obj.loan_items.count()
    items_count.short_description = 'Total Items'

    def borrowed_count(self, obj):
        return obj.loan_items.filter(status='borrowed').count()
    borrowed_count.short_description = 'Borrowed'

    def returned_count(self, obj):
        return obj.loan_items.filter(status='returned').count()
    returned_count.short_description = 'Returned'

    def lost_count(self, obj):
        return obj.loan_items.filter(status='lost').count()
    lost_count.short_description = 'Lost'


@admin.register(LoanItem)
class LoanItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'batch_user', 'batch_due_date', 'reservation', 'status', 'returned_at', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'returned_at', 'updated_at', 'loan_batch__due_date')
    search_fields = (
        'id',
        'book__title',
        'loan_batch__user__username',
        'loan_batch__user__email',
        'loan_batch__user__first_name',
        'loan_batch__user__last_name'
    )
    date_hierarchy = 'created_at'
    autocomplete_fields = ['book', 'loan_batch', 'reservation']
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_returned', 'mark_as_lost']
    list_select_related = ['book', 'loan_batch', 'loan_batch__user', 'reservation']
    list_per_page = 20
    
    fieldsets = (
        ('Loan Item Information', {
            'fields': ('book', 'loan_batch', 'reservation', 'status', 'returned_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def batch_user(self, obj):
        return obj.loan_batch.user.username
    batch_user.short_description = 'User'
    batch_user.admin_order_field = 'loan_batch__user__username'

    def batch_due_date(self, obj):
        return obj.loan_batch.due_date
    batch_due_date.short_description = 'Due Date'
    batch_due_date.admin_order_field = 'loan_batch__due_date'

    @admin.action(description='Mark selected items as Returned')
    def mark_as_returned(self, request, queryset):
        """Mark loan items as returned and update book availability."""
        success_count = 0
        error_count = 0
        errors = []

        for loan_item in queryset:
            try:
                with transaction.atomic():
                    # Check if already returned or lost
                    if loan_item.status == 'returned':
                        errors.append(f"Loan Item #{loan_item.id} ({loan_item.book.title}) is already returned.")
                        error_count += 1
                        continue
                    
                    if loan_item.status == 'lost':
                        errors.append(f"Loan Item #{loan_item.id} ({loan_item.book.title}) is marked as lost. Cannot mark as returned.")
                        error_count += 1
                        continue

                    # Update loan item status
                    loan_item.status = 'returned'
                    loan_item.returned_at = timezone.now()
                    loan_item.save()

                    # Increase available_quantity
                    book = loan_item.book
                    book.available_quantity += 1
                    book.save()

                    success_count += 1

            except Exception as e:
                errors.append(f"Error processing Loan Item #{loan_item.id}: {str(e)}")
                error_count += 1

        # Display messages
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully marked {success_count} loan item(s) as returned.",
                messages.SUCCESS
            )
        
        if error_count > 0:
            for error in errors:
                self.message_user(request, error, messages.ERROR)
            self.message_user(
                request,
                f"Failed to process {error_count} loan item(s).",
                messages.WARNING
            )

    @admin.action(description='Mark selected items as Lost')
    def mark_as_lost(self, request, queryset):
        """Mark loan items as lost. Lost books do NOT increase available_quantity."""
        success_count = 0
        error_count = 0
        errors = []

        for loan_item in queryset:
            try:
                with transaction.atomic():
                    # Check if already returned
                    if loan_item.status == 'returned':
                        errors.append(f"Loan Item #{loan_item.id} ({loan_item.book.title}) is already returned. Cannot mark as lost.")
                        error_count += 1
                        continue
                    
                    # Check if already lost
                    if loan_item.status == 'lost':
                        errors.append(f"Loan Item #{loan_item.id} ({loan_item.book.title}) is already marked as lost.")
                        error_count += 1
                        continue

                    # Update loan item status
                    loan_item.status = 'lost'
                    loan_item.save()

                    # NOTE: Do NOT increase available_quantity for lost books
                    # Admin may need to manually create a Fine for this lost item

                    success_count += 1

            except Exception as e:
                errors.append(f"Error processing Loan Item #{loan_item.id}: {str(e)}")
                error_count += 1

        # Display messages
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully marked {success_count} loan item(s) as lost. Remember to create fines for lost items.",
                messages.SUCCESS
            )
        
        if error_count > 0:
            for error in errors:
                self.message_user(request, error, messages.ERROR)
            self.message_user(
                request,
                f"Failed to process {error_count} loan item(s).",
                messages.WARNING
            )
