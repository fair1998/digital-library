from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta
from .models import LoanBatch, LoanItem
from reservations.models import ReservationBatch, Reservation
from books.models import Book


@login_required
def my_loans_view(request):
    """
    Display user's loan history.
    """
    loan_batches = LoanBatch.objects.filter(
        user=request.user
    ).prefetch_related(
        'loan_items__book__authors',
        'loan_items__book__publisher'
    ).order_by('-created_at')
    
    # Calculate if loans are overdue
    now = timezone.now()
    for batch in loan_batches:
        batch.is_overdue = batch.due_date and batch.due_date < now if batch.due_date else False
        for item in batch.loan_items.all():
            item.is_overdue = batch.is_overdue and item.status == 'borrowed'
    
    context = {
        'loan_batches': loan_batches,
    }
    
    return render(request, 'loans/my_loans.html', context)


# Admin views
def is_staff(user):
    """Check if user is staff/admin."""
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def create_loan_view(request, batch_id):
    """
    Create a loan from a confirmed reservation batch.
    This happens when user comes to pick up the books.
    """
    reservation_batch = get_object_or_404(
        ReservationBatch.objects.prefetch_related(
            'reservations__book__authors',
            'reservations__book__publisher'
        ),
        id=batch_id
    )
    
    # Validate that batch is confirmed
    if reservation_batch.status != 'confirmed':
        messages.error(request, 'การจองนี้ยังไม่ได้รับการยืนยันหรือถูกยกเลิกแล้ว')
        return redirect('dashboard_reservations')
    
    # Check if expired
    if reservation_batch.is_expired():
        messages.error(request, 'การจองนี้หมดอายุแล้ว กรุณายกเลิกการจองและให้ user จองใหม่')
        return redirect('dashboard_reservations')
    
    if request.method == 'POST':
        # Get loan period from settings or default 14 days
        loan_days = getattr(settings, 'LOAN_PERIOD_DAYS', 14)
        
        # Get additional books from POST data
        additional_book_ids = request.POST.getlist('additional_books')
        
        try:
            with transaction.atomic():
                # Create loan batch
                loan_batch = LoanBatch.objects.create(
                    user=reservation_batch.user,
                    due_date=timezone.now() + timedelta(days=loan_days)
                )
                
                # Create loan items from confirmed reservations
                confirmed_reservations = reservation_batch.reservations.filter(
                    status='confirmed'
                )
                
                for reservation in confirmed_reservations:
                    LoanItem.objects.create(
                        book=reservation.book,
                        loan_batch=loan_batch,
                        reservation=reservation,
                        status='borrowed'
                    )
                
                # Create loan items for additional books
                if additional_book_ids:
                    for book_id in additional_book_ids:
                        try:
                            book = Book.objects.get(id=book_id)
                            
                            # Check if book is available
                            if book.available_quantity <= 0:
                                raise ValueError(f'หนังสือ "{book.title}" ไม่มีในคลัง')
                            
                            # Decrease available quantity
                            book.available_quantity -= 1
                            book.save()
                            
                            # Create loan item (no reservation link for additional books)
                            LoanItem.objects.create(
                                book=book,
                                loan_batch=loan_batch,
                                reservation=None,
                                status='borrowed'
                            )
                        except Book.DoesNotExist:
                            raise ValueError(f'ไม่พบหนังสือ ID: {book_id}')
                
                # Update reservation batch status to completed
                reservation_batch.status = 'completed'
                reservation_batch.save()
                
                total_books = confirmed_reservations.count() + len(additional_book_ids)
                messages.success(
                    request,
                    f'สร้างรายการยืมสำเร็จ! ยืมทั้งหมด {total_books} เล่ม กำหนดคืนวันที่ {loan_batch.due_date.strftime("%d/%m/%Y")}'
                )
                return redirect('loans:active_loans')
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
            return redirect('dashboard_reservations')
    
    # GET request - show confirmation page
    confirmed_reservations = reservation_batch.reservations.filter(
        status='confirmed'
    )
    
    context = {
        'reservation_batch': reservation_batch,
        'reservations': confirmed_reservations,
    }
    
    return render(request, 'loans/create_loan.html', context)


@login_required
@user_passes_test(is_staff)
def active_loans_view(request):
    """
    Display all active loans (borrowed status).
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base query
    loan_batches = LoanBatch.objects.select_related('user').prefetch_related(
        'loan_items__book__authors',
        'loan_items__book__publisher'
    )

    # Apply filters
    if status_filter and status_filter != 'all':
        loan_batches = loan_batches.filter(loan_items__status=status_filter).distinct()
    
    if search_query:
        q_filter = Q(user__username__icontains=search_query)
        # If search query is a number, also search by batch ID
        if search_query.isdigit():
            q_filter |= Q(id=int(search_query))
        loan_batches = loan_batches.filter(q_filter).distinct()
    
    loan_batches = loan_batches.order_by('-created_at')
    
    # Calculate overdue status
    now = timezone.now()
    for batch in loan_batches:
        batch.is_overdue = batch.due_date and batch.due_date < now
        for item in batch.loan_items.all():
            item.is_overdue = batch.is_overdue and item.status == 'borrowed'
    
    context = {
        'loan_batches': loan_batches,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'loans/active_loans.html', context)


@login_required
@user_passes_test(is_staff)
def loan_detail_view(request, batch_id):
    """
    Display loan batch details with actions to mark items as returned or lost.
    """
    loan_batch = get_object_or_404(
        LoanBatch.objects.select_related('user').prefetch_related(
            'loan_items__book__authors',
            'loan_items__book__publisher',
            'loan_items__reservation__reservation_batch'
        ),
        id=batch_id
    )
    
    # Calculate overdue
    now = timezone.now()
    loan_batch.is_overdue = loan_batch.due_date and loan_batch.due_date < now
    
    for item in loan_batch.loan_items.all():
        item.is_overdue = loan_batch.is_overdue and item.status == 'borrowed'
    
    context = {
        'loan_batch': loan_batch,
    }
    
    return render(request, 'loans/loan_detail.html', context)


@login_required
@user_passes_test(is_staff)
def mark_returned_view(request, item_id):
    """
    Mark a loan item as returned.
    """
    loan_item = get_object_or_404(LoanItem, id=item_id)
    
    if loan_item.status != 'borrowed':
        messages.error(request, 'หนังสือเล่มนี้ไม่ได้อยู่ในสถานะยืมแล้ว')
    else:
        try:
            with transaction.atomic():
                # Update loan item
                loan_item.status = 'returned'
                loan_item.returned_at = timezone.now()
                loan_item.save()
                
                # Increase available quantity
                book = loan_item.book
                book.available_quantity += 1
                book.save()
                
                messages.success(request, f'บันทึกการคืนหนังสือ "{book.title}" สำเร็จ')
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('loans:loan_detail', batch_id=loan_item.loan_batch.id)


@login_required
@user_passes_test(is_staff)
def mark_lost_view(request, item_id):
    """
    Mark a loan item as lost.
    Note: Lost items do NOT increase available_quantity.
    """
    loan_item = get_object_or_404(LoanItem, id=item_id)
    
    if loan_item.status != 'borrowed':
        messages.error(request, 'หนังสือเล่มนี้ไม่ได้อยู่ในสถานะยืมแล้ว')
    else:
        try:
            with transaction.atomic():
                # Update loan item
                loan_item.status = 'lost'
                loan_item.returned_at = timezone.now()  # Record when it was marked as lost
                loan_item.save()
                
                # Decrease total quantity since book is permanently lost
                book = loan_item.book
                book.total_quantity -= 1
                book.save()
                
                messages.warning(
                    request,
                    f'บันทึกหนังสือหาย "{book.title}" สำเร็จ - จำนวนทั้งหมดถูกลดลง 1 เล่ม'
                )
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('loans:loan_detail', batch_id=loan_item.loan_batch.id)


@login_required
@user_passes_test(is_staff)
def search_books_api(request):
    """
    API endpoint for searching books (for adding additional books to loan).
    Returns JSON with book data.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'books': []})
    
    # Search books by title or authors
    books = Book.objects.filter(
        Q(title__icontains=query) |
        Q(authors__name__icontains=query)
    ).select_related('publisher').prefetch_related('authors').distinct()[:10]
    
    books_data = []
    for book in books:
        authors_str = ', '.join([author.name for author in book.authors.all()])
        books_data.append({
            'id': book.id,
            'title': book.title,
            'authors': authors_str,
            'publisher': book.publisher.name if book.publisher else '',
            'available_quantity': book.available_quantity,
        })
    
    return JsonResponse({'books': books_data})
