from django.contrib import admin
from .models import Author, Book, BookAuthor, BookCategory, Category, Publisher


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("id", "name")
    list_filter = ("created_at",)
    ordering = ("id",)
    list_per_page = 50


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("id", "name")
    list_filter = ("created_at",)
    ordering = ("id",)
    list_per_page = 50


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("id", "name")
    list_filter = ("created_at",)
    ordering = ("id",)
    list_per_page = 50


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "isbn",
        "image_url",
        "total_quantity",
        "available_quantity",
        "publish_year",
        "publisher",
        "created_at",
    )
    search_fields = ("id", "title", "isbn", "description")
    list_filter = ("publish_year", "publisher", "created_at")
    ordering = ("id",)
    list_per_page = 50


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "author")
    search_fields = ("id",)
    list_filter = ("book", "author")
    ordering = ("id",)
    list_per_page = 50


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "category")
    search_fields = ("id",)
    list_filter = ("book", "category")
    ordering = ("id",)
    list_per_page = 50