from django.contrib import admin
from .models import Loan, LoanItem


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'due_date', 'created_at')
    search_fields = ('id',)
    list_filter = ('status', 'created_at')
    ordering = ('id',)
    list_per_page = 50


@admin.register(LoanItem)
class LoanItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'loan', 'hold_item', 'status', 'returned_at', 'created_at')
    search_fields = ('id',)
    list_filter = ('status', 'created_at')
    ordering = ('id',)
    list_per_page = 50
