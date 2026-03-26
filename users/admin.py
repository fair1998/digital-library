from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):    
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    )
    search_fields = ("id", "username", "email", "first_name", "last_name", "phone_number")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups", "date_joined")
    ordering = ("-date_joined",)
    list_per_page = 20

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone_number",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("phone_number",)}),
    )
