from django.db import models
from django.db.models import Q


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Keep table name aligned with docs/data_dictionary.md.
        db_table = "authors"
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Keep table name aligned with docs/data_dictionary.md.
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Keep table name aligned with docs/data_dictionary.md.
        db_table = "publishers"
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    isbn = models.CharField(
        max_length=13,
        unique=True,
        null=False,
        blank=False,
    )
    description = models.TextField(null=True, blank=True)
    # Stored as a file path (Django will manage actual storage backend; later can be swapped to S3).
    image_url = models.ImageField(
        upload_to="books/covers/",
        max_length=255,
        null=True,
        blank=True,
    )

    total_quantity = models.IntegerField(default=0)
    available_quantity = models.IntegerField(default=0)

    # Nullable YEAR with check >= 0 (when provided).
    publish_year = models.IntegerField(null=True, blank=True)

    publisher = models.ForeignKey(
        "Publisher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    authors = models.ManyToManyField(
        "Author",
        through="BookAuthor",
        related_name="books",
    )
    categories = models.ManyToManyField(
        "Category",
        through="BookCategory",
        related_name="books",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Keep table name aligned with docs/data_dictionary.md.
        db_table = "books"
        verbose_name = "Book"
        verbose_name_plural = "Books"
        constraints = [
            models.CheckConstraint(
                check=Q(total_quantity__gte=0),
                name="check_books_total_quantity_gte_0",
            ),
            models.CheckConstraint(
                check=Q(available_quantity__gte=0),
                name="check_books_available_quantity_gte_0",
            ),
            models.CheckConstraint(
                check=Q(publish_year__isnull=True) | Q(publish_year__gte=0),
                name="check_books_publish_year_gte_0_or_null",
            ),
        ]

    def __str__(self) -> str:
        return self.title


class BookAuthor(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)

    class Meta:
        # Keep table name aligned with docs/data_dictionary.md.
        db_table = "book_authors"
        verbose_name = "Book Author"
        verbose_name_plural = "Book Authors"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "author"],
                name="unique_book_author",
            )
        ]

    def __str__(self) -> str:
        return f"{self.book} - {self.author}"


class BookCategory(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    class Meta:
        # Keep table name aligned with docs/data_dictionary.md.
        db_table = "book_categories"
        verbose_name = "Book Category"
        verbose_name_plural = "Book Categories"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "category"],
                name="unique_book_category",
            )
        ]

    def __str__(self) -> str:
        return f"{self.book} - {self.category}"