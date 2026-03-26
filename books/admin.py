from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Author, Book, BookAuthor, BookCategory, Category, Publisher


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1
    autocomplete_fields = ("author",)


class BookCategoryInline(admin.TabularInline):
    model = BookCategory
    extra = 1
    autocomplete_fields = ("category",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "books_count", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    ordering = ("name",)
    list_per_page = 20

    def get_queryset(self, request):
        # Annotate counts to avoid N+1 queries in list_display.
        return super().get_queryset(request).annotate(
            books_count=Count("books", distinct=True)
        )

    @admin.display(description="Books")
    def books_count(self, obj):
        # get_queryset() provides books_count.
        return getattr(obj, "books_count", 0)

    readonly_fields = ("created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "books_count", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    ordering = ("name",)
    list_per_page = 20

    def get_queryset(self, request):
        # Annotate counts to avoid N+1 queries in list_display.
        return super().get_queryset(request).annotate(
            books_count=Count("books", distinct=True)
        )

    @admin.display(description="Books")
    def books_count(self, obj):
        # get_queryset() provides books_count.
        return getattr(obj, "books_count", 0)

    readonly_fields = ("created_at", "updated_at")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "books_count", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at")
    ordering = ("name",)
    list_per_page = 20

    def get_queryset(self, request):
        # Book.publisher uses related_name="book" for reverse relation.
        return super().get_queryset(request).annotate(
            books_count=Count("book", distinct=True)
        )

    @admin.display(description="Books")
    def books_count(self, obj):
        return getattr(obj, "books_count", 0)

    readonly_fields = ("created_at", "updated_at")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cover_preview",
        "title",
        "publisher",
        "publish_year",
        "total_quantity",
        "available_quantity",
        "availability_status",
        "author_names",
        "category_names",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "id",
        "title",
        "description",
        "authors__name",
        "categories__name",
        "publisher__name",
    )
    list_filter = ("publish_year", "publisher", "available_quantity", "authors", "categories", "created_at")
    autocomplete_fields = ("publisher",)
    ordering = ("-created_at",)
    list_select_related = ("publisher",)
    list_per_page = 20
    inlines = [BookAuthorInline, BookCategoryInline]
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'description', 'image_url', 'publisher', 'publish_year')
        }),
        ('Inventory', {
            'fields': ('total_quantity', 'available_quantity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("authors", "categories")

    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Cover")
    def cover_preview(self, obj):
        if not obj.image_url:
            return "-"
        try:
            return format_html(
                '<img src="{}" style="height:50px; width:auto;" />',
                obj.image_url.url,
            )
        except ValueError:
            # In case the file field has no usable URL yet.
            return "-"

    @admin.display(description="Availability")
    def availability_status(self, obj):
        return "Available" if obj.available_quantity > 0 else "Unavailable"

    @admin.display(description="Authors")
    def author_names(self, obj):
        return ", ".join(author.name for author in obj.authors.all()) or "-"

    @admin.display(description="Categories")
    def category_names(self, obj):
        return ", ".join(category.name for category in obj.categories.all()) or "-"


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "author")
    search_fields = ("book__title", "author__name")
    list_filter = ("author", "book")
    ordering = ("book__title", "author__name")
    list_select_related = ("book", "author")
    autocomplete_fields = ("book", "author")
    list_per_page = 50


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "category")
    search_fields = ("book__title", "category__name")
    list_filter = ("category", "book")
    ordering = ("category__name", "book__title")
    list_select_related = ("book", "category")
    autocomplete_fields = ("book", "category")
    list_per_page = 50