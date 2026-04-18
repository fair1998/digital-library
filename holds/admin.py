from django.contrib import admin
from .models import Hold, HoldItem


@admin.register(Hold)
class HoldAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'expires_at', 'created_at')
    search_fields = ('id',)
    list_filter = ('status', 'created_at')
    ordering = ('id',)
    list_per_page = 50


@admin.register(HoldItem)
class HoldItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'hold', 'status', 'created_at')
    search_fields = ('id',)
    list_filter = ('status', 'created_at')
    ordering = ('id',)
    list_per_page = 50
