from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book, Category, Publisher


def book_list_view(request):
    """
    Display list of all books with search and filter functionality.
    """
    books = Book.objects.all().select_related('publisher').prefetch_related('authors', 'categories')
    
    # Search by title
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(title__icontains=search_query)
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        books = books.filter(categories__id=category_id)
    
    # Filter by publisher
    publisher_id = request.GET.get('publisher', '')
    if publisher_id:
        books = books.filter(publisher__id=publisher_id)
    
    # Order by title
    books = books.order_by('title').distinct()
    
    # Pagination
    paginator = Paginator(books, 12)  # 12 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories and publishers for filter dropdowns
    categories = Category.objects.all().order_by('name')
    publishers = Publisher.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_publisher': publisher_id,
        'categories': categories,
        'publishers': publishers,
    }
    
    return render(request, 'books/book_list.html', context)


def book_detail_view(request, book_id):
    """
    Display detailed information about a specific book.
    """
    book = get_object_or_404(
        Book.objects.select_related('publisher').prefetch_related('authors', 'categories'),
        id=book_id
    )
    
    context = {
        'book': book,
    }
    
    return render(request, 'books/book_detail.html', context)
