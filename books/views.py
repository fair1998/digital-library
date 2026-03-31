from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Book, Category, Publisher
from reservations.models import ReservationBatch, Reservation
from .cart import Cart


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


@login_required
def reserve_book_view(request, book_id):
    """
    DEPRECATED: This view is replaced by add_to_cart + confirm_cart workflow.
    Kept for backward compatibility but should not be used.
    """
    messages.warning(request, 'กรุณาใช้ระบบตะกร้าสำหรับการจองหนังสือ')
    return redirect('books:book_detail', book_id=book_id)


@login_required
def add_to_cart_view(request, book_id):
    """
    Add a book to the reservation cart.
    """
    from django.http import JsonResponse
    
    if request.method != 'POST':
        # For AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/x-www-form-urlencoded':
            return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
        messages.error(request, 'Invalid request method.')
        return redirect('books:book_detail', book_id=book_id)
    
    book = get_object_or_404(Book, id=book_id)
    
    # Check if book is available
    if book.available_quantity <= 0:
        # For AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'X-CSRFToken' in request.headers:
            return JsonResponse({'success': False, 'message': f'ขออภัย หนังสือ "{book.title}" ไม่มีให้จองในขณะนี้'}, status=400)
        messages.error(request, f'ขออภัย หนังสือ "{book.title}" ไม่มีให้จองในขณะนี้')
        return redirect('books:book_detail', book_id=book_id)
    
    # Add to cart
    cart = Cart(request)
    was_added = cart.add(book_id)
    
    # For AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'X-CSRFToken' in request.headers:
        return JsonResponse({
            'success': True,
            'added': was_added,
            'cart_count': cart.count(),
            'message': f'เพิ่ม "{book.title}" ไปยังตะกร้าแล้ว' if was_added else f'"{book.title}" อยู่ในตะกร้าอยู่แล้ว'
        })
    
    # For regular form submissions
    if was_added:
        messages.success(request, f'เพิ่ม "{book.title}" ไปยังตะกร้าแล้ว')
    else:
        messages.info(request, f'"{book.title}" อยู่ในตะกร้าอยู่แล้ว')
    
    return redirect('books:book_detail', book_id=book_id)


@login_required
def view_cart(request):
    """
    Display cart contents.
    """
    cart = Cart(request)
    book_ids = cart.get_book_ids()
    
    # Get book details
    books = Book.objects.filter(id__in=book_ids).select_related('publisher').prefetch_related('authors', 'categories')
    
    # Create a list with availability check
    cart_items = []
    has_unavailable = False
    for book in books:
        is_available = book.available_quantity > 0
        if not is_available:
            has_unavailable = True
        cart_items.append({
            'book': book,
            'is_available': is_available,
        })
    
    context = {
        'cart_items': cart_items,
        'cart_count': cart.count(),
        'has_unavailable': has_unavailable,
    }
    
    return render(request, 'books/cart.html', context)


@login_required
def remove_from_cart_view(request, book_id):
    """
    Remove a book from cart.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('books:view_cart')
    
    book = get_object_or_404(Book, id=book_id)
    cart = Cart(request)
    
    if cart.remove(book_id):
        messages.success(request, f'ลบ "{book.title}" ออกจากตะกร้าแล้ว')
    else:
        messages.error(request, 'ไม่พบหนังสือในตะกร้า')
    
    return redirect('books:view_cart')


@login_required
def confirm_cart_view(request):
    """
    Confirm reservation for all books in cart.
    Creates a ReservationBatch with multiple Reservation items.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('books:view_cart')
    
    cart = Cart(request)
    book_ids = cart.get_book_ids()
    
    if not book_ids:
        messages.warning(request, 'ตะกร้าของคุณว่างเปล่า')
        return redirect('books:view_cart')
    
    try:
        with transaction.atomic():
            # Get all books and check availability
            books = Book.objects.filter(id__in=book_ids).select_for_update()
            
            unavailable_books = []
            for book in books:
                if book.available_quantity <= 0:
                    unavailable_books.append(book.title)
            
            if unavailable_books:
                messages.error(
                    request,
                    f'ไม่สามารถจองได้เนื่องจากหนังสือต่อไปนี้ไม่มีให้ยืม: {", ".join(unavailable_books)}'
                )
                return redirect('books:view_cart')
            
            # Create reservation batch
            # Note: expires_at will be set by admin when confirming
            reservation_batch = ReservationBatch.objects.create(
                user=request.user,
                status='pending',
                expires_at=None  # Admin will set this when confirming
            )
            
            # Create reservation items
            for book in books:
                Reservation.objects.create(
                    book=book,
                    reservation_batch=reservation_batch,
                    status='pending'
                )
            
            # Clear cart
            cart.clear()
            
            messages.success(
                request,
                f'จองหนังสือ {len(books)} เล่มสำเร็จ! '
                f'กรุณารอการยืนยันจากเจ้าหน้าที่'
            )
            return redirect('reservations:my_reservations')
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาดในการจองหนังสือ: {str(e)}')
        return redirect('books:view_cart')
