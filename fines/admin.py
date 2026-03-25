from django.contrib import admin
from .models import Fine


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'loan_item',
        'type',
        'amount',
        'status',
        'paid_at',
        'created_at'
    ]
    list_filter = ['type', 'status', 'created_at', 'paid_at']
    search_fields = ['loan_item__book__title', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    
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
