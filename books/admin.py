from django.contrib import admin
from .models import Author, Category, Publisher, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 20


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 20


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 20


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "publisher",
        "publish_year",
        "total_quantity",
        "available_quantity",
        "author_names",
        "category_names",
        "updated_at",
    )
    search_fields = ("title", "description", "authors__name", "categories__name", "publisher__name")
    list_filter = ("publish_year", "publisher", "categories", "authors")
    filter_horizontal = ("authors", "categories")
    ordering = ("-created_at",)
    list_select_related = ("publisher",)
    list_per_page = 20

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("authors", "categories")

    @admin.display(description="Authors")
    def author_names(self, obj):
        return ", ".join(author.name for author in obj.authors.all()) or "-"

    @admin.display(description="Categories")
    def category_names(self, obj):
        return ", ".join(category.name for category in obj.categories.all()) or "-"