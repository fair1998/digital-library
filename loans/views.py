from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal
from .models import Loan, LoanItem
from holds.models import Hold
from books.models import Book
from fines.models import Fine


@login_required
def my_loans_view(request):
    """
    Display user's loan history.
    """
    loans = Loan.objects.filter(
        user=request.user
    ).prefetch_related(
        'loan_items__book__authors',
        'loan_items__book__publisher'
    ).order_by('-created_at')
    
    context = {
        'loan_batches': loans,
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
    Create a loan from a confirmed hold batch.
    This happens when user comes to pick up the books.
    """
    hold = get_object_or_404(
        Hold.objects.prefetch_related(
            'hold_items__book__authors',
            'hold_items__book__publisher'
        ),
        id=batch_id
    )
    
    # Validate that batch is confirmed
    if hold.status != 'confirmed':
        messages.error(request, 'การจองนี้ยังไม่ได้รับการยืนยันหรือถูกยกเลิกแล้ว')
        return redirect('holds:dashboard_holds')
    
    # Check if expired
    if hold.is_expired:
        messages.error(request, 'การจองนี้หมดอายุแล้ว กรุณายกเลิกการจองและให้ user จองใหม่')
        return redirect('holds:dashboard_holds')
    
    if request.method == 'POST':
        # Get loan period from settings or default 14 days
        loan_days = getattr(settings, 'LOAN_PERIOD_DAYS', 14)
        
        # Get additional books from POST data
        additional_book_ids = request.POST.getlist('additional_books')
        
        try:
            with transaction.atomic():
                # Create loan batch
                loan_batch = Loan.objects.create(
                    user=hold.user,
                    due_date=timezone.now() + timedelta(days=loan_days)
                )
                
                # Create loan items from confirmed hold items
                confirmed_hold_items = hold.hold_items.filter(
                    status='confirmed'
                )
                
                for hold_item in confirmed_hold_items:
                    LoanItem.objects.create(
                        book=hold_item.book,
                        loan=loan_batch,
                        hold_item=hold_item,
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
                            
                            # Create loan item (no hold item link for additional books)
                            LoanItem.objects.create(
                                book=book,
                                loan=loan_batch,
                                hold_item=None,
                                status='borrowed'
                            )
                        except Book.DoesNotExist:
                            raise ValueError(f'ไม่พบหนังสือ ID: {book_id}')
                
                # Update hold status to completed
                hold.status = 'completed'
                hold.save()
                
                total_books = confirmed_hold_items.count() + len(additional_book_ids)
                messages.success(
                    request,
                    f'สร้างรายการยืมสำเร็จ! ยืมทั้งหมด {total_books} เล่ม กำหนดคืนวันที่ {loan_batch.due_date.strftime("%d/%m/%Y")}'
                )
                return redirect('loans:active_loans')
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
            return redirect('holds:dashboard_holds')
    
    # GET request - show confirmation page
    confirmed_hold_items = hold.hold_items.filter(
        status='confirmed'
    )
    
    context = {
        'hold': hold,
        'hold_items': confirmed_hold_items,
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
    loan_batches = Loan.objects.select_related('user').prefetch_related(
        'loan_items__book__authors',
        'loan_items__book__publisher'
    )

    # Apply filters
    if status_filter and status_filter != 'all':
        loan_batches = loan_batches.filter(status=status_filter)
    
    if search_query:
        q_filter = Q(user__username__icontains=search_query)
        # If search query is a number, also search by batch ID
        if search_query.isdigit():
            q_filter |= Q(id=int(search_query))
        loan_batches = loan_batches.filter(q_filter).distinct()
    
    loan_batches = loan_batches.order_by('-created_at')
    
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
        Loan.objects.select_related('user').prefetch_related(
            'loan_items__book__authors',
            'loan_items__book__publisher',
            'loan_items__hold_item__hold'
        ),
        id=batch_id
    )
    
    context = {
        'loan_batch': loan_batch,
    }
    
    return render(request, 'loans/loan_detail.html', context)


@login_required
@user_passes_test(is_staff)
def mark_returned_view(request, item_id):
    """
    Mark a loan item as returned.
    Handles both regular returns and returns with damage.
    If POST with is_damaged=true, creates a damage fine.
    """
    loan_item = get_object_or_404(LoanItem, id=item_id)
    
    if loan_item.status != 'borrowed':
        messages.error(request, 'หนังสือเล่มนี้ไม่ได้อยู่ในสถานะยืมแล้ว')
        return redirect('loans:loan_detail', batch_id=loan_item.loan.id)
    
    # Check if this is a damage report
    if request.method == 'POST':
        is_damaged = request.POST.get('is_damaged') == 'true'
        damage_amount = request.POST.get('damage_amount', '').strip()
        damage_reason = request.POST.get('damage_reason', '').strip()
        
        # Validate damage data if damaged
        if is_damaged:
            if not damage_amount or not damage_reason:
                messages.error(request, 'กรุณากรอกจำนวนเงินและเหตุผลสำหรับความเสียหาย')
                return redirect('loans:loan_detail', batch_id=loan_item.loan.id)
            
            try:
                damage_amount = Decimal(damage_amount)
                if damage_amount <= 0:
                    messages.error(request, 'จำนวนเงินต้องมากกว่า 0')
                    return redirect('loans:loan_detail', batch_id=loan_item.loan.id)
            except (ValueError, TypeError):
                messages.error(request, 'จำนวนเงินไม่ถูกต้อง')
                return redirect('loans:loan_detail', batch_id=loan_item.loan.id)
        
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
                
                # Track if any fine was created
                fine_created = False
                
                # Create late return fine if overdue
                loan_batch = loan_item.loan
                if loan_batch.due_date and loan_item.returned_at.date() > loan_batch.due_date.date():
                    days_late = (loan_item.returned_at.date() - loan_batch.due_date.date()).days
                    fine_per_day = Decimal(getattr(settings, 'FINE_LATE_RETURN_PER_DAY', 10))
                    late_fine_amount = fine_per_day * days_late
                    
                    Fine.objects.create(
                        loan_item=loan_item,
                        type='late_return',
                        amount=late_fine_amount,
                        reason=f'คืนช้า {days_late} วัน (กำหนดคืน: {loan_batch.due_date.strftime("%d/%m/%Y")})',
                        status='unpaid'
                    )
                    messages.warning(
                        request,
                        f'สร้างค่าปรับคืนช้า {days_late} วัน จำนวน {late_fine_amount} บาท'
                    )
                    fine_created = True
                
                # Create damage fine if damaged
                if is_damaged:
                    Fine.objects.create(
                        loan_item=loan_item,
                        type='damaged',
                        amount=damage_amount,
                        reason=damage_reason,
                        status='unpaid'
                    )
                    messages.warning(
                        request,
                        f'สร้างค่าปรับหนังสือเสียหาย จำนวน {damage_amount} บาท'
                    )
                    fine_created = True
                
                # Check if all items in the batch are completed
                all_completed = not loan_batch.loan_items.filter(status='borrowed').exists()
                if all_completed:
                    loan_batch.status = 'completed'
                    loan_batch.save()
                
                messages.success(request, f'บันทึกการคืนหนังสือ "{book.title}" สำเร็จ')
                
                # Redirect to fines report if fine was created
                if fine_created:
                    return redirect('dashboard_fines:admin_report')
                    
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('loans:loan_detail', batch_id=loan_item.loan.id)


@login_required
@user_passes_test(is_staff)
def mark_lost_view(request, item_id):
    """
    Mark a loan item as lost.
    Note: Lost items do NOT increase available_quantity.
    Automatically creates a lost fine.
    """
    loan_item = get_object_or_404(LoanItem, id=item_id)
    
    if loan_item.status != 'borrowed':
        messages.error(request, 'หนังสือเล่มนี้ไม่ได้อยู่ในสถานะยืมแล้ว')
        return redirect('loans:loan_detail', batch_id=loan_item.loan.id)
    
    if request.method == 'POST':
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
                
                # Create lost fine
                loan_batch = loan_item.loan
                lost_fine_amount = Decimal(getattr(settings, 'FINE_LOST_BOOK', 500))
                
                Fine.objects.create(
                    loan_item=loan_item,
                    type='lost',
                    amount=lost_fine_amount,
                    reason=f'ทำหนังสือหาย: {book.title}',
                    status='unpaid'
                )
                
                # Check if all items in the batch are completed
                all_completed = not loan_batch.loan_items.filter(status='borrowed').exists()
                if all_completed:
                    loan_batch.status = 'completed'
                    loan_batch.save()
                
                messages.warning(
                    request,
                    f'บันทึกหนังสือหาย "{book.title}" สำเร็จ - สร้างค่าปรับ {lost_fine_amount} บาท'
                )
                
                # Redirect to fines report
                return redirect('dashboard_fines:admin_report')
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('loans:loan_detail', batch_id=loan_item.loan.id)


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


@login_required
@user_passes_test(is_staff)
def process_batch_return_view(request, batch_id):
    """
    Process batch return/lost with immediate fine payment.
    Handles multiple books at once with damage/lost information.
    """
    loan = get_object_or_404(
        Loan.objects.select_related('user').prefetch_related(
            'loan_items__book'
        ),
        id=batch_id
    )
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                now = timezone.now()
                total_fine_amount = Decimal('0.00')
                returned_count = 0
                lost_count = 0
                
                # Get all loan items that are still borrowed
                borrowed_items = loan.loan_items.filter(status='borrowed')
                
                for item in borrowed_items:
                    action = request.POST.get(f'action_{item.id}')
                    
                    if action == 'return':
                        # Process return
                        item.status = 'returned'
                        item.returned_at = now
                        item.save()
                        
                        # Increase available quantity
                        item.book.available_quantity += 1
                        item.book.save()
                        
                        returned_count += 1
                        
                        # Check for late return fine
                        if loan.due_date and now.date() > loan.due_date.date():
                            days_late = (now.date() - loan.due_date.date()).days
                            late_fine_per_day = Decimal(getattr(settings, 'FINE_LATE_RETURN_PER_DAY', 10))
                            late_fine_amount = late_fine_per_day * days_late
                            
                            Fine.objects.create(
                                loan_item=item,
                                type='late_return',
                                amount=late_fine_amount,
                                reason=f'คืนช้า {days_late} วัน',
                                paid_at=now
                            )
                            total_fine_amount += late_fine_amount
                        
                        # Check for damage fine
                        is_damaged = request.POST.get(f'damaged_{item.id}') == 'true'
                        if is_damaged:
                            damage_amount = Decimal(request.POST.get(f'damage_amount_{item.id}', 0))
                            damage_reason = request.POST.get(f'damage_reason_{item.id}', '')
                            
                            if damage_amount > 0:
                                Fine.objects.create(
                                    loan_item=item,
                                    type='damaged',
                                    amount=damage_amount,
                                    reason=damage_reason,
                                    paid_at=now
                                )
                                total_fine_amount += damage_amount
                    
                    elif action == 'lost':
                        # Process lost
                        item.status = 'lost'
                        item.save()
                        
                        lost_count += 1
                        
                        # Create lost fine
                        lost_fine_amount = Decimal(getattr(settings, 'FINE_LOST_BOOK', 500))
                        Fine.objects.create(
                            loan_item=item,
                            type='lost',
                            amount=lost_fine_amount,
                            reason=f'ทำหนังสือหาย: {item.book.title}',
                            paid_at=now
                        )
                        total_fine_amount += lost_fine_amount
                
                # Check if all items in batch are completed
                all_completed = not loan.loan_items.filter(status='borrowed').exists()
                if all_completed:
                    loan.status = 'completed'
                    loan.save()
                
                # Create success message
                msg_parts = []
                if returned_count > 0:
                    msg_parts.append(f'คืนแล้ว {returned_count} เล่ม')
                if lost_count > 0:
                    msg_parts.append(f'หาย {lost_count} เล่ม')
                if total_fine_amount > 0:
                    msg_parts.append(f'ค่าปรับรวม {total_fine_amount} บาท (ชำระแล้ว)')
                
                messages.success(request, 'ดำเนินการสำเร็จ: ' + ', '.join(msg_parts))
                
                return redirect('loans:loan_detail', batch_id=loan.id)
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
            return redirect('loans:loan_detail', batch_id=loan.id)
    
    # GET request - should not reach here (handled in template)
    return redirect('loans:loan_detail', batch_id=loan.id)
