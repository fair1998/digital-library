from django.contrib import admin
from .models import LoanBatch, LoanItem


class LoanItemInline(admin.TabularInline):
    model = LoanItem
    extra = 1
    fields = ('book', 'reservation', 'status', 'returned_at')
    autocomplete_fields = ['book', 'reservation']


@admin.register(LoanBatch)
class LoanBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'due_date', 'created_at', 'get_items_count')
    list_filter = ('created_at', 'due_date')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    autocomplete_fields = ['user']
    inlines = [LoanItemInline]
    readonly_fields = ('created_at', 'updated_at')
    
    # ปิดการสร้างใหม่จาก admin (ให้สร้างผ่าน frontend เท่านั้น)
    def has_add_permission(self, request):
        return False
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('user', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_items_count(self, obj):
        return obj.loan_items.count()
    get_items_count.short_description = 'Items Count'


@admin.register(LoanItem)
class LoanItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'loan_batch', 'status', 'returned_at', 'created_at')
    list_filter = ('status', 'created_at', 'returned_at')
    search_fields = (
        'book__title',
        'loan_batch__user__username',
        'loan_batch__user__email'
    )
    date_hierarchy = 'created_at'
    autocomplete_fields = ['book', 'loan_batch', 'reservation']
    readonly_fields = ('created_at', 'updated_at')
    
    # ปิดการสร้างใหม่จาก admin (LoanItem ควรสร้างผ่าน LoanBatch inline หรือ frontend)
    def has_add_permission(self, request):
        return False
    
    fieldsets = (
        ('Loan Item Information', {
            'fields': ('book', 'loan_batch', 'reservation', 'status', 'returned_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
