from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "citizen_id",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    )
    search_fields = ("id", "username", "email", "phone_number", "citizen_id")
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined")
    ordering = ("id",)
    list_per_page = 50
