from django.contrib import admin
from .models import Fine


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('id', 'loan_item', 'type', 'amount', 'reason', 'paid_at')
    search_fields = ('id', 'reason')
    list_filter = ('type', 'paid_at')
    ordering = ('id',)
    list_per_page = 50
