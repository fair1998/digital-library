from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from .models import Book, Category, Publisher , Author
from holds.models import Hold, HoldItem
from .cart import Cart
from .forms import (
    DashboardAuthorForm,
    DashboardBookForm,
    DashboardCategoryForm,
    DashboardPublisherForm,
)

def book_list_view(request):
    """
    Display list of all books with search and filter functionality.
    """
    books = Book.objects.all().select_related('publisher').prefetch_related('authors', 'categories')
    
    # Search by title
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
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
    messages.warning(request, 'กรุณาใช้ระบบรายการจองสำหรับการจองหนังสือ')
    return redirect('books:book_detail', book_id=book_id)


@login_required
def add_to_cart_view(request, book_id):
    """
    Add a book to the hold item cart.
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
            'message': f'เพิ่ม "{book.title}" ลงรายการจองแล้ว' if was_added else f'"{book.title}" อยู่ในรายการจองอยู่แล้ว'
        })
    
    # For regular form submissions
    if was_added:
        messages.success(request, f'เพิ่ม "{book.title}" ลงรายการจองแล้ว')
    else:
        messages.warning(request, f'"{book.title}" อยู่ในรายการจองอยู่แล้ว')
    
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
        messages.success(request, f'ลบ "{book.title}" ออกจากรายการจองแล้ว')
    else:
        messages.error(request, 'ไม่พบหนังสือในรายการจอง')
    
    return redirect('books:view_cart')


@login_required
def confirm_cart_view(request):
    """
    Confirm hold for all books in cart.
    Creates a Hold with multiple HoldItem items.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('books:view_cart')
    
    cart = Cart(request)
    book_ids = cart.get_book_ids()
    
    if not book_ids:
        messages.warning(request, 'รายการจองของคุณว่างเปล่า')
        return redirect('books:view_cart')
    
    # Check maximum books per user limit
    from django.conf import settings
    max_books = getattr(settings, 'MAX_BOOKS_PER_USER', 10)
    current_borrowed = request.user.get_current_borrowed_count()
    new_books_count = len(book_ids)
    
    if current_borrowed + new_books_count > max_books:
        messages.error(
            request,
            f'ไม่สามารถจองได้ คุณกำลังยืมหนังสืออยู่ {current_borrowed} เล่ม '
            f'และพยายามจองเพิ่ม {new_books_count} เล่ม '
            f'ซึ่งจะเกินจำนวนสูงสุด {max_books} เล่มที่สามารถยืมพร้อมกันได้'
        )
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
            
            # Create hold
            # Note: expires_at will be set by admin when confirming
            holds = Hold.objects.create(
                user=request.user,
                status='pending',
                expires_at=None  # Admin will set this when confirming
            )
            
            # Create hold items
            for book in books:
                HoldItem.objects.create(
                    book=book,
                    hold=holds,
                    status='pending'
                )
            
            # Clear cart
            cart.clear()
            
            messages.success(
                request,
                f'จองหนังสือ {len(books)} เล่มสำเร็จ! '
                f'กรุณารอการยืนยันจากเจ้าหน้าที่'
            )
            return redirect('holds:my_holds')
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาดในการจองหนังสือ: {str(e)}')
        return redirect('books:view_cart')

@staff_member_required
def dashboard_books_view(request):
    """
    Admin dashboard view for managing books.
    """
    books = Book.objects.all().select_related('publisher').prefetch_related('authors', 'categories')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )

    author_id = request.GET.get('author', '').strip()
    if author_id:
        books = books.filter(authors__id=author_id)

    category_id = request.GET.get('category', '').strip()
    if category_id:
        books = books.filter(categories__id=category_id)

    publisher_id = request.GET.get('publisher', '').strip()
    if publisher_id:
        books = books.filter(publisher__id=publisher_id)

    sort_by = request.GET.get('sort', 'title').strip()
    allowed_sorts = {
        'title': 'title',
        '-title': '-title',
        '-created_at': '-created_at',
        'created_at': 'created_at',
        '-available_quantity': '-available_quantity',
        'available_quantity': 'available_quantity',
        '-total_quantity': '-total_quantity',
        'total_quantity': 'total_quantity',
        '-publish_year': '-publish_year',
        'publish_year': 'publish_year',
    }
    sort_order = allowed_sorts.get(sort_by, 'title')

    books = books.order_by(sort_order).distinct()

    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    authors = Author.objects.all().order_by('name')
    categories = Category.objects.all().order_by('name')
    publishers = Publisher.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'authors': authors,
        'categories': categories,
        'publishers': publishers,
        'search_query': search_query,
        'selected_author': author_id,
        'selected_category': category_id,
        'selected_publisher': publisher_id,
        'sort_by': sort_by,
    }
    
    return render(request, 'dashboard/books/list.html', context)


@staff_member_required
def dashboard_book_detail_view(request, book_id):
    """
    Admin dashboard view for displaying detailed information about a book.
    """
    book = get_object_or_404(
        Book.objects.select_related('publisher').prefetch_related('authors', 'categories'),
        id=book_id
    )
    
    # Get confirmed hold items (books reserved and confirmed by admin)
    # Must check both Hold.status='confirmed' AND HoldItem.status='confirmed'
    confirmed_holds = book.hold_items.filter(
        hold__status='confirmed',
        status='confirmed'
    ).select_related('hold__user').order_by('-created_at')
    
    # Get borrowed loan items (books currently being borrowed)
    # Must check both Loan.status='active' AND LoanItem.status='borrowed'
    borrowed_loans = book.loan_items.filter(
        loan__status='active',
        status='borrowed'
    ).select_related('loan__user', 'loan').order_by('-created_at')
    
    # Get lost loan items
    lost_loans = book.loan_items.filter(
        status='lost'
    ).select_related('loan__user', 'loan').order_by('-created_at')
    
    # Calculate book distribution
    confirmed_holds_count = confirmed_holds.count()
    borrowed_loans_count = borrowed_loans.count()
    lost_loans_count = lost_loans.count()
    
    # Calculate accounted books (not including lost books as they're already deducted from total)
    accounted_books = book.available_quantity + confirmed_holds_count + borrowed_loans_count
    
    context = {
        'book': book,
        'confirmed_holds': confirmed_holds,
        'borrowed_loans': borrowed_loans,
        'lost_loans': lost_loans,
        'confirmed_holds_count': confirmed_holds_count,
        'borrowed_loans_count': borrowed_loans_count,
        'lost_loans_count': lost_loans_count,
        'accounted_books': accounted_books,
    }
    
    return render(request, 'dashboard/books/detail.html', context)


@staff_member_required
def dashboard_book_form_view(request):
    """
    Admin dashboard view for creating a new book.
    """
    if request.method == 'POST':
        form = DashboardBookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มหนังสือเรียบร้อยแล้ว')
            return redirect('books:dashboard_books')
    else:
        form = DashboardBookForm()

    context = {
        'form': form,
        'form_title': 'เพิ่มหนังสือ',
        'book': None,
    }
    return render(request, 'dashboard/books/form.html', context)


@staff_member_required
def dashboard_books_form_id_view(request, book_id):
    """
    Admin dashboard view for editing an existing book.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = DashboardBookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'บันทึกข้อมูลหนังสือเรียบร้อยแล้ว')
            return redirect('books:dashboard_books')
    else:
        form = DashboardBookForm(instance=book)

    context = {
        'form': form,
        'form_title': 'แก้ไขหนังสือ',
        'book': book,
    }
    return render(request, 'dashboard/books/form.html', context)


@staff_member_required
def dashboard_book_delete_view(request, book_id):
    """
    Admin dashboard action for deleting a book.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('books:dashboard_books')

    book = get_object_or_404(Book, id=book_id)

    if book.hold_items.exists() or book.loan_items.exists():
        messages.error(
            request,
            f'ไม่สามารถลบ "{book.title}" ได้ เนื่องจากมีประวัติการจองหรือการยืมอยู่ในระบบ'
        )
        return redirect('books:dashboard_books')

    title = book.title
    book.delete()
    messages.success(request, f'ลบหนังสือ "{title}" เรียบร้อยแล้ว')
    return redirect('books:dashboard_books')

@staff_member_required
def dashboard_authors_view(request):
    """
    Admin dashboard view for managing authors.
    """
    authors = Author.objects.annotate(books_count=Count('books', distinct=True))

    search_query = request.GET.get('search', '').strip()
    if search_query:
        authors = authors.filter(name__icontains=search_query)

    has_books = request.GET.get('has_books', '').strip()
    if has_books == 'yes':
        authors = authors.filter(books_count__gt=0)
    elif has_books == 'no':
        authors = authors.filter(books_count=0)

    sort_by = request.GET.get('sort', 'name').strip()
    allowed_sorts = {
        'name': 'name',
        '-name': '-name',
        '-created_at': '-created_at',
        'created_at': 'created_at',
        '-books_count': '-books_count',
        'books_count': 'books_count',
    }
    authors = authors.order_by(allowed_sorts.get(sort_by, 'name'), 'id')

    paginator = Paginator(authors, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'entity_label': 'ผู้แต่ง',
        'entity_icon': 'bi-person',
        'add_url_name': 'books:dashboard_author_form',
        'edit_url_name': 'books:dashboard_author_form_id',
        'delete_url_name': 'books:dashboard_author_delete',
        'page_obj': page_obj,
        'search_query': search_query,
        'has_books': has_books,
        'sort_by': sort_by,
    }
    return render(request, 'dashboard/library_entities/list.html', context)

@staff_member_required
def dashboard_categories_view(request):
    """
    Admin dashboard view for managing categories.
    """
    categories = Category.objects.annotate(books_count=Count('books', distinct=True))

    search_query = request.GET.get('search', '').strip()
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    has_books = request.GET.get('has_books', '').strip()
    if has_books == 'yes':
        categories = categories.filter(books_count__gt=0)
    elif has_books == 'no':
        categories = categories.filter(books_count=0)

    sort_by = request.GET.get('sort', 'name').strip()
    allowed_sorts = {
        'name': 'name',
        '-name': '-name',
        '-created_at': '-created_at',
        'created_at': 'created_at',
        '-books_count': '-books_count',
        'books_count': 'books_count',
    }
    categories = categories.order_by(allowed_sorts.get(sort_by, 'name'), 'id')

    paginator = Paginator(categories, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'entity_label': 'หมวดหมู่',
        'entity_icon': 'bi-tags',
        'add_url_name': 'books:dashboard_category_form',
        'edit_url_name': 'books:dashboard_category_form_id',
        'delete_url_name': 'books:dashboard_category_delete',
        'page_obj': page_obj,
        'search_query': search_query,
        'has_books': has_books,
        'sort_by': sort_by,
    }
    return render(request, 'dashboard/library_entities/list.html', context)

@staff_member_required
def dashboard_publishers_view(request):
    """
    Admin dashboard view for managing publishers.
    """
    publishers = Publisher.objects.annotate(books_count=Count('books', distinct=True))

    search_query = request.GET.get('search', '').strip()
    if search_query:
        publishers = publishers.filter(name__icontains=search_query)

    has_books = request.GET.get('has_books', '').strip()
    if has_books == 'yes':
        publishers = publishers.filter(books_count__gt=0)
    elif has_books == 'no':
        publishers = publishers.filter(books_count=0)

    sort_by = request.GET.get('sort', 'name').strip()
    allowed_sorts = {
        'name': 'name',
        '-name': '-name',
        '-created_at': '-created_at',
        'created_at': 'created_at',
        '-books_count': '-books_count',
        'books_count': 'books_count',
    }
    publishers = publishers.order_by(allowed_sorts.get(sort_by, 'name'), 'id')

    paginator = Paginator(publishers, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'entity_label': 'สำนักพิมพ์',
        'entity_icon': 'bi-building',
        'add_url_name': 'books:dashboard_publisher_form',
        'edit_url_name': 'books:dashboard_publisher_form_id',
        'delete_url_name': 'books:dashboard_publisher_delete',
        'page_obj': page_obj,
        'search_query': search_query,
        'has_books': has_books,
        'sort_by': sort_by,
    }
    return render(request, 'dashboard/library_entities/list.html', context)


@staff_member_required
def dashboard_author_form_view(request):
    if request.method == 'POST':
        form = DashboardAuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มผู้แต่งเรียบร้อยแล้ว')
            return redirect('books:dashboard_authors')
    else:
        form = DashboardAuthorForm()

    return render(request, 'dashboard/library_entities/form.html', {
        'form': form,
        'form_title': 'เพิ่มผู้แต่ง',
        'entity_label': 'ผู้แต่ง',
        'entity_icon': 'bi-person',
        'back_url_name': 'books:dashboard_authors',
    })


@staff_member_required
def dashboard_author_form_id_view(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    if request.method == 'POST':
        form = DashboardAuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'บันทึกข้อมูลผู้แต่งเรียบร้อยแล้ว')
            return redirect('books:dashboard_authors')
    else:
        form = DashboardAuthorForm(instance=author)

    return render(request, 'dashboard/library_entities/form.html', {
        'form': form,
        'form_title': 'แก้ไขผู้แต่ง',
        'entity_label': 'ผู้แต่ง',
        'entity_icon': 'bi-person',
        'back_url_name': 'books:dashboard_authors',
    })


@staff_member_required
def dashboard_author_delete_view(request, author_id):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('books:dashboard_authors')

    author = get_object_or_404(Author, id=author_id)

    name = author.name
    author.delete()
    messages.success(request, f'ลบผู้แต่ง "{name}" เรียบร้อยแล้ว')
    return redirect('books:dashboard_authors')


@staff_member_required
def dashboard_category_form_view(request):
    if request.method == 'POST':
        form = DashboardCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มหมวดหมู่เรียบร้อยแล้ว')
            return redirect('books:dashboard_categories')
    else:
        form = DashboardCategoryForm()

    return render(request, 'dashboard/library_entities/form.html', {
        'form': form,
        'form_title': 'เพิ่มหมวดหมู่',
        'entity_label': 'หมวดหมู่',
        'entity_icon': 'bi-tags',
        'back_url_name': 'books:dashboard_categories',
    })


@staff_member_required
def dashboard_category_form_id_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = DashboardCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'บันทึกข้อมูลหมวดหมู่เรียบร้อยแล้ว')
            return redirect('books:dashboard_categories')
    else:
        form = DashboardCategoryForm(instance=category)

    return render(request, 'dashboard/library_entities/form.html', {
        'form': form,
        'form_title': 'แก้ไขหมวดหมู่',
        'entity_label': 'หมวดหมู่',
        'entity_icon': 'bi-tags',
        'back_url_name': 'books:dashboard_categories',
    })


@staff_member_required
def dashboard_category_delete_view(request, category_id):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('books:dashboard_categories')

    category = get_object_or_404(Category, id=category_id)

    name = category.name
    category.delete()
    messages.success(request, f'ลบหมวดหมู่ "{name}" เรียบร้อยแล้ว')
    return redirect('books:dashboard_categories')


@staff_member_required
def dashboard_publisher_form_view(request):
    if request.method == 'POST':
        form = DashboardPublisherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มสำนักพิมพ์เรียบร้อยแล้ว')
            return redirect('books:dashboard_publishers')
    else:
        form = DashboardPublisherForm()

    return render(request, 'dashboard/library_entities/form.html', {
        'form': form,
        'form_title': 'เพิ่มสำนักพิมพ์',
        'entity_label': 'สำนักพิมพ์',
        'entity_icon': 'bi-building',
        'back_url_name': 'books:dashboard_publishers',
    })


@staff_member_required
def dashboard_publisher_form_id_view(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    if request.method == 'POST':
        form = DashboardPublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            messages.success(request, 'บันทึกข้อมูลสำนักพิมพ์เรียบร้อยแล้ว')
            return redirect('books:dashboard_publishers')
    else:
        form = DashboardPublisherForm(instance=publisher)

    return render(request, 'dashboard/library_entities/form.html', {
        'form': form,
        'form_title': 'แก้ไขสำนักพิมพ์',
        'entity_label': 'สำนักพิมพ์',
        'entity_icon': 'bi-building',
        'back_url_name': 'books:dashboard_publishers',
    })


@staff_member_required
def dashboard_publisher_delete_view(request, publisher_id):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('books:dashboard_publishers')

    publisher = get_object_or_404(Publisher, id=publisher_id)

    name = publisher.name
    publisher.delete()
    messages.success(request, f'ลบสำนักพิมพ์ "{name}" เรียบร้อยแล้ว')
    return redirect('books:dashboard_publishers')

def get_books_api(request):
    """
    API endpoint for searching books
    Returns JSON with book data.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'books': []})
    
    # Search books by title or ISBN
    books = Book.objects.filter(
        Q(title__icontains=query) |
        Q(isbn__icontains=query)
    ).distinct()[:10]
    
    books_data = []
    for book in books:
        books_data.append({
            'id': book.id,
            'title': book.title,
            'isbn': book.isbn,
            'image_url': book.image_url.url if book.image_url else '',
        })
    
    return JsonResponse({'books': books_data})


@staff_member_required
def api_create_author(request):
    """
    API endpoint for creating a new author via modal.
    """
    import json
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'กรุณากรอกชื่อผู้แต่ง'})
        
        # Check if author already exists
        if Author.objects.filter(name=name).exists():
            return JsonResponse({'success': False, 'error': 'ผู้แต่งนี้มีอยู่ในระบบแล้ว'})
        
        author = Author.objects.create(name=name)
        
        return JsonResponse({
            'success': True,
            'author': {
                'id': author.id,
                'name': author.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
def api_create_category(request):
    """
    API endpoint for creating a new category via modal.
    """
    import json
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'กรุณากรอกชื่อหมวดหมู่'})
        
        # Check if category already exists
        if Category.objects.filter(name=name).exists():
            return JsonResponse({'success': False, 'error': 'หมวดหมู่นี้มีอยู่ในระบบแล้ว'})
        
        category = Category.objects.create(name=name)
        
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
def api_create_publisher(request):
    """
    API endpoint for creating a new publisher via modal.
    """
    import json
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'กรุณากรอกชื่อสำนักพิมพ์'})
        
        # Check if publisher already exists
        if Publisher.objects.filter(name=name).exists():
            return JsonResponse({'success': False, 'error': 'สำนักพิมพ์นี้มีอยู่ในระบบแล้ว'})
        
        publisher = Publisher.objects.create(name=name)
        
        return JsonResponse({
            'success': True,
            'publisher': {
                'id': publisher.id,
                'name': publisher.name
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})