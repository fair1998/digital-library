from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta

from loans.models import Loan, LoanItem
from .models import Hold, HoldItem
from books.models import Book


@login_required
def my_holds_view(request):
    """
    Display user's hold item history.
    """
    holds_list = Hold.objects.filter(
        user=request.user
    ).prefetch_related(
        'hold_items__book__authors',
        'hold_items__book__publisher'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(holds_list, 10)  # Show 10 holds per page
    page = request.GET.get('page')
    
    try:
        holds = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        holds = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        holds = paginator.page(paginator.num_pages)
    
    context = {
        'holds': holds,
    }
    
    return render(request, 'holds/list.html', context)


@login_required
def cancel_hold_view(request, hold_id):
    """
    Allow user to cancel their own pending hold item batch.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('holds:my_holds')
    
    # Get batch and verify ownership
    hold = get_object_or_404(Hold, id=hold_id, user=request.user)
    
    # Check if user can cancel
    if not hold.can_be_cancelled_by_user:
        messages.error(
            request,
            f'ไม่สามารถยกเลิกการจอง #{hold.id} ได้ (สถานะ: {hold.status_label})'
        )
        return redirect('holds:my_holds')
    
    try:
        with transaction.atomic():
            # Update batch status
            hold.status = 'cancelled'
            hold.save()
            
            # Update all hold items
            for hold_item in hold.hold_items.all():
                hold_item.status = 'cancelled'
                hold_item.save()
            
            messages.success(
                request,
                f'ยกเลิกการจอง #{hold.id} สำเร็จ ({hold.hold_items.count()} เล่ม)'
            )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('holds:my_hold_list')


@staff_member_required
def dashboard_holds_view(request):
    """
    Admin dashboard to manage all hold batches.
    Shows pending, confirmed, completed, cancelled, and expired holds.
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    batch_id_filter = request.GET.get('batch_id', '').strip()
    user_filter = request.GET.get('user', '').strip()
    
    # Base queryset
    holds = Hold.objects.select_related(
        'user'
    ).prefetch_related(
        'hold_items__book__authors',
        'hold_items__book__publisher'
    ).order_by('-created_at')
    
    # Apply batch ID filter
    if batch_id_filter:
        holds = holds.filter(id=batch_id_filter)
    
    # Apply user filter (search by username, first name, or last name)
    if user_filter:
        from django.db.models import Q
        holds = holds.filter(
            Q(user__username__icontains=user_filter) |
            Q(user__first_name__icontains=user_filter) |
            Q(user__last_name__icontains=user_filter)
        )
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        holds = holds.filter(status=status_filter)
    
    # Add expiry info to each batch and collect expired confirmed batches
    expired_batches = []
    for batch in holds:
        # Collect only CONFIRMED batches that expired (customer didn't pick up)
        if batch.is_expired and batch.status == 'confirmed':
            expired_batches.append(batch)

    
    status_choices = Hold.STATUS_CHOICES
    
    # Count stats for dashboard
    stats = {
        "status_choices": status_choices,
        'total': Hold.objects.count(),
        'pending': Hold.objects.filter(status='pending').count(),
        'confirmed': Hold.objects.filter(status='confirmed').count(),
        'completed': Hold.objects.filter(status='completed').count(),
        'expired_pending': len(expired_batches),  # Confirmed ที่หมดอายุแต่ยังไม่ได้จัดการ
        'expired': Hold.objects.filter(status='expired').count(),  # ที่เปลี่ยน status เป็น expired แล้ว
        'cancelled': Hold.objects.filter(status='cancelled').count(),
    }
    
    context = {
        'holds': holds,
        'status_filter': status_filter,
        'batch_id_filter': batch_id_filter,
        'user_filter': user_filter,
        'stats': stats,
        'expired_batches': expired_batches,
    }
    
    return render(request, 'dashboard/holds/list.html', context)


@staff_member_required
def dashboard_hold_detail_view(request, hold_id):
    """
    Display detailed view of a hold batch with ability to manage individual items.
    """
    hold = get_object_or_404(
        Hold.objects.select_related('user').prefetch_related(
            'hold_items__book__authors',
            'hold_items__book__publisher'
        ),
        id=hold_id
    )
    
    # Check stock availability
    has_out_of_stock = False
    has_available_books = False
    for hold_item in hold.hold_items.all():
        if hold_item.book.available_quantity == 0:
            has_out_of_stock = True
        else:
            has_available_books = True

    
    context = {
        'batch': hold,
        'has_out_of_stock': has_out_of_stock,
        'has_available_books': has_available_books,
    }
    
    return render(request, 'dashboard/holds/detail.html', context)


@staff_member_required
def dashboard_confirm_hold_books_view(request, hold_id):
    """
    Admin action to confirm selected hold items.
    Unselected items will be automatically rejected/cancelled.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('holds:dashboard_holds')
    
    hold = get_object_or_404(Hold, id=hold_id)
    
    # Check if can be confirmed
    if hold.status != 'pending':
        messages.error(
            request,
            f'ไม่สามารถยืนยันการจอง #{hold.id} ได้ (สถานะ: {hold.status_label})'
        )
        return redirect('holds:dashboard_hold_detail', hold_id=hold_id)
    
    # Get selected hold item IDs
    selected_ids = request.POST.getlist('hold_item_ids')
    
    if not selected_ids:
        messages.warning(request, 'กรุณาเลือกหนังสือที่ต้องการยืนยัน')
        return redirect('holds:dashboard_hold_detail', hold_id=hold_id)
    
    try:
        with transaction.atomic():
            # Get all pending hold items
            all_pending = hold.hold_items.filter(status='pending').select_related('book')
            
            # Get selected hold items to confirm
            selected_hold_items = all_pending.filter(id__in=selected_ids)
            
            # Get unselected hold items (to be rejected)
            unselected_hold_items = all_pending.exclude(id__in=selected_ids)
            
            # Check availability for selected books
            insufficient_books = []
            confirmed_count = 0
            
            for hold_item in selected_hold_items:
                if hold_item.book.available_quantity < 1:
                    insufficient_books.append(hold_item.book.title)
                else:
                    # Confirm this hold item
                    hold_item.status = 'confirmed'
                    hold_item.save()
                    
                    # Decrease available quantity
                    book = hold_item.book
                    book.available_quantity -= 1
                    book.save()
                    
                    confirmed_count += 1
            
            # Reject all unselected items
            rejected_count = 0
            for hold_item in unselected_hold_items:
                hold_item.status = 'cancelled'
                hold_item.save()
                rejected_count += 1
            
            # Update batch status
            has_confirmed = hold.hold_items.filter(status='confirmed').exists()
            all_processed = not hold.hold_items.filter(status='pending').exists()
            
            if has_confirmed:
                hold.status = 'confirmed'
                # Set expiry time for confirmed hold (user must pick up books before this time)
                expiry_days = getattr(settings, 'HOLD_EXPIRY_DAYS', 3)
                hold.expires_at = timezone.now() + timedelta(days=expiry_days)
                hold.save()
            elif all_processed:
                hold.status = 'cancelled'
                hold.save()
            
            # Build success message
            msg_parts = []
            if confirmed_count > 0:
                msg_parts.append(f'ยืนยัน {confirmed_count} เล่ม')
            if rejected_count > 0:
                msg_parts.append(f'ยกเลิก {rejected_count} เล่ม')
            
            messages.success(
                request,
                f'ดำเนินการสำเร็จ: {", ".join(msg_parts)}'
            )
            
            if insufficient_books:
                messages.warning(
                    request,
                    f'ไม่สามารถยืนยันหนังสือต่อไปนี้ได้ (สต็อคไม่พอ): {", ".join(insufficient_books)}'
                )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('holds:dashboard_hold_detail', hold_id=hold_id)

@staff_member_required
def dashboard_cancel_hold_view(request, hold_id):
    """
    Admin action to cancel a hold item batch.
    If expired, mark as 'expired', otherwise 'cancelled'.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('holds:dashboard_holds')
    
    hold = get_object_or_404(Hold, id=hold_id)
    
    # Check if already finalized
    if hold.status in ['cancelled', 'expired', 'completed']:
        messages.warning(request, f'การจอง #{hold.id} ถูกจัดการไปแล้ว (สถานะ: {hold.status_label})')
        return redirect('holds:dashboard_holds')
    
    # Check if this is an expired cancellation
    is_expired_cancellation = hold.is_expired and hold.status == 'confirmed'
    
    try:
        with transaction.atomic():
            # Store old status for message
            old_status = hold.status_label
            
            # If was confirmed, need to return book quantities
            if hold.status == 'confirmed':
                for hold_item in hold.hold_items.filter(status='confirmed'):
                    book = hold_item.book
                    book.available_quantity += 1
                    book.save()
            
            # Update batch status based on reason
            if is_expired_cancellation:
                hold.status = 'expired'
                new_status = 'หมดอายุ (ลูกค้าไม่มารับ)'
            else:
                hold.status = 'cancelled'
                new_status = 'ยกเลิก'
            
            hold.save()
            
            messages.success(
                request,
                f'{new_status}การจอง #{hold.id} สำเร็จ (สถานะเดิม: {old_status}, User: {hold.user.username})'
            )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('holds:dashboard_holds')

@staff_member_required
def dashboard_create_loan_from_hold_view(request, hold_id):
    """
    Create a loan from a confirmed hold batch.
    This happens when user comes to pick up the books.
    """
    hold = get_object_or_404(
        Hold.objects.prefetch_related(
            'hold_items__book__authors',
            'hold_items__book__publisher'
        ),
        id=hold_id
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
        # Get loan period from settings or default 7 days
        loan_days = getattr(settings, 'LOAN_PERIOD_DAYS', 7)
        
        # Calculate due date (end of day in Bangkok timezone)
        # Django will convert to UTC automatically when saving to DB
        local_now = timezone.localtime(timezone.now())
        due_date = (local_now + timedelta(days=loan_days)).replace(
            hour=23, minute=59, second=59, microsecond=0
        )
        
        # Get additional books from POST data
        additional_book_ids = request.POST.getlist('additional_books')
        
        # Check maximum books per user limit
        max_books = getattr(settings, 'MAX_BOOKS_PER_USER', 10)
        current_borrowed = hold.user.get_current_borrowed_count()
        confirmed_hold_items_count = hold.hold_items.filter(status='confirmed').count()
        new_books_count = confirmed_hold_items_count + len(additional_book_ids)
        
        if current_borrowed + new_books_count > max_books:
            messages.error(
                request,
                f'ไม่สามารถยืมได้ ผู้ใช้ {hold.user.username} กำลังยืมหนังสืออยู่ {current_borrowed} เล่ม '
                f'และจะยืมเพิ่ม {new_books_count} เล่ม ซึ่งจะเกินจำนวนสูงสุด {max_books} เล่ม'
            )
            return redirect('holds:dashboard_hold_detail', hold_id=hold.id)
        
        try:
            with transaction.atomic():
                # Create loan batch
                loan_batch = Loan.objects.create(
                    user=hold.user,
                    due_date=due_date
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
                return redirect('loans:dashboard_loans')
                
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
    
    return render(request, 'dashboard/holds/create_loan_from_hold.html', context)
