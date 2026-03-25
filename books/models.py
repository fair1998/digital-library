from django.db import models

# Create your models here.
class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "authors"
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Publisher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "publishers"
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"

    def __str__(self):
        return self.name

class Book(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image_url = models.ImageField(upload_to="books/covers/", null=True, blank=True)
    total_quantity = models.IntegerField(default=0)
    available_quantity = models.IntegerField(default=0)
    publish_year = models.IntegerField(null=True, blank=True)
    publisher = models.ForeignKey(
        "Publisher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="publisher_id",
    )

    # 🔥 ใช้ ManyToManyField แทนตารางกลาง
    authors = models.ManyToManyField(
        Author,
        related_name="books",
    )

    categories = models.ManyToManyField(
        Category,
        related_name="books"
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books"
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return self.title

# class BookAuthor(models.Model):
#     id = models.AutoField(primary_key=True)
#     book = models.ForeignKey(
#         "Book",
#         on_delete=models.CASCADE,
#         db_column="book_id",
#     )
#     author = models.ForeignKey(
#         "Author",
#         on_delete=models.CASCADE,
#         db_column="author_id",
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = "book_authors"
#         verbose_name = "Book Author"
#         verbose_name_plural = "Book Authors"
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["book", "author"],
#                 name="unique_book_author",
#             )
#         ]

#     def __str__(self):
#         return f"{self.book} - {self.author}"

# class BookCategory(models.Model):
#     id = models.AutoField(primary_key=True)
#     book = models.ForeignKey(
#         "Book",
#         on_delete=models.CASCADE,
#         db_column="book_id",
#     )
#     category = models.ForeignKey(
#         "Category",
#         on_delete=models.CASCADE,
#         db_column="category_id",
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = "book_categories"
#         verbose_name = "Book Category"
#         verbose_name_plural = "Book Categories"
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["book", "category"],
#                 name="unique_book_category",
#             )
#         ]

#     def __str__(self):
#         return f"{self.book} - {self.category}"