from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from decimal import Decimal
from .models import Loan, LoanItem
from books.models import Book
from fines.models import Fine
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def my_loans_view(request):
    """
    Display user's loan history.
    """
    loans_list = Loan.objects.filter(
        user=request.user
    ).prefetch_related(
        'loan_items__book__authors',
        'loan_items__book__publisher'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(loans_list, 10)  # Show 10 loans per page
    page = request.GET.get('page')
    
    try:
        loan_batches = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        loan_batches = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        loan_batches = paginator.page(paginator.num_pages)
    
    context = {
        'loan_batches': loan_batches,
    }
    
    return render(request, 'loans/my_loans.html', context)


@login_required
@staff_member_required
def dashboard_loans_view(request):
    """
    Display all active loans (borrowed status).
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_id = request.GET.get('search_id', '').strip()
    search_user = request.GET.get('search_user', '').strip()
    
    # Base query
    loan_batches = Loan.objects.select_related('user').prefetch_related(
        'loan_items__book__authors',
        'loan_items__book__publisher'
    )

    # Apply filters
    if status_filter and status_filter != 'all':
        loan_batches = loan_batches.filter(status=status_filter)
    
    # Apply ID search filter
    if search_id:
        if search_id.isdigit():
            loan_batches = loan_batches.filter(id=int(search_id))
    
    # Apply user search filter (citizen_id, username, email, full name, phone)
    if search_user:
        from django.db.models import Value, CharField
        from django.db.models.functions import Concat
        
        # Build search filter for user fields
        q_filter = Q()
        q_filter |= Q(user__citizen_id__icontains=search_user)
        q_filter |= Q(user__username__icontains=search_user)
        q_filter |= Q(user__email__icontains=search_user)
        q_filter |= Q(user__first_name__icontains=search_user)
        q_filter |= Q(user__last_name__icontains=search_user)
        q_filter |= Q(user__phone_number__icontains=search_user)
        
        # Annotate full name and add to search
        loan_batches = loan_batches.annotate(
            user_full_name=Concat('user__first_name', Value(' '), 'user__last_name', output_field=CharField())
        ).filter(q_filter | Q(user_full_name__icontains=search_user)).distinct()
    
    loan_batches = loan_batches.order_by('-created_at')
    
    context = {
        'status_choices': Loan.STATUS_CHOICES,
        'loan_batches': loan_batches,
        'status_filter': status_filter,
        'search_id': search_id,
        'search_user': search_user,
    }
    
    return render(request, 'dashboard/loans/list.html', context)


@login_required
@staff_member_required
def dashboard_create_loan_view(request):
    """
    Create a new loan directly (without hold).
    Admin can select user and books to create a loan.
    """
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get user
                user_id = request.POST.get('user_id')
                if not user_id:
                    messages.error(request, 'กรุณาเลือกผู้ใช้')
                    return redirect('loans:dashboard_create_loan')
                
                user = get_object_or_404(User, id=user_id)
                
                # Get book IDs
                book_ids = request.POST.getlist('book_ids')
                if not book_ids:
                    messages.error(request, 'กรุณาเลือกหนังสืออย่างน้อย 1 เล่ม')
                    return redirect('loans:dashboard_create_loan')
                
                # Check maximum books per user limit
                max_books = getattr(settings, 'MAX_BOOKS_PER_USER', 10)
                current_borrowed = user.get_current_borrowed_count()
                new_books_count = len(book_ids)
                
                if current_borrowed + new_books_count > max_books:
                    messages.error(
                        request,
                        f'ไม่สามารถยืมได้ ผู้ใช้ {user.username} กำลังยืมหนังสืออยู่ {current_borrowed} เล่ม '
                        f'และจะยืมเพิ่ม {new_books_count} เล่ม ซึ่งจะเกินจำนวนสูงสุด {max_books} เล่ม'
                    )
                    return redirect('loans:dashboard_create_loan')
                
                # Calculate due date from settings (end of day in Bangkok timezone)
                # Django will convert to UTC automatically when saving to DB
                loan_period_days = getattr(settings, 'LOAN_PERIOD_DAYS', 7)
                local_now = timezone.localtime(timezone.now())
                due_date = (local_now + timedelta(days=loan_period_days)).replace(
                    hour=23, minute=59, second=59, microsecond=0
                )
                
                # Get books and validate availability
                books = Book.objects.filter(id__in=book_ids)
                
                if books.count() != len(book_ids):
                    messages.error(request, 'พบหนังสือที่ไม่ถูกต้อง')
                    return redirect('loans:dashboard_create_loan')
                
                # Check availability
                unavailable_books = []
                for book in books:
                    if book.available_quantity <= 0:
                        unavailable_books.append(book.title)
                
                if unavailable_books:
                    messages.error(request, f'หนังสือต่อไปนี้ไม่ว่าง: {", ".join(unavailable_books)}')
                    return redirect('loans:dashboard_create_loan')
                
                # Create Loan
                loan = Loan.objects.create(
                    user=user,
                    status='active',
                    due_date=due_date
                )
                
                # Create LoanItems and update book quantities
                for book in books:
                    LoanItem.objects.create(
                        loan=loan,
                        book=book,
                        status='borrowed',
                        hold_item=None  # No hold item for direct loan
                    )
                    
                    # Decrease available quantity
                    book.available_quantity -= 1
                    book.save()
                
                messages.success(request, f'สร้างรายการยืมสำเร็จ (Loan #{loan.id}) - {books.count()} เล่ม')
                return redirect('loans:dashboard_loan_detail', loan_id=loan.id)
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
            return redirect('loans:dashboard_create_loan')
    
    # GET request - show form
    context = {
        'LOAN_PERIOD_DAYS': getattr(settings, 'LOAN_PERIOD_DAYS', 7),
    }
    return render(request, 'dashboard/loans/create_loan.html', context)


@login_required
@staff_member_required
def dashboard_loan_detail_view(request, loan_id):
    """
    Display loan batch details with actions to mark items as returned or lost.
    """
    loan = get_object_or_404(
        Loan.objects.select_related('user').prefetch_related(
            'loan_items__book__authors',
            'loan_items__book__publisher',
            'loan_items__hold_item__hold'
        ),
        id=loan_id
    )
    
    # Check if there are any borrowed items
    has_borrowed_items = loan.loan_items.filter(status='borrowed').exists()
    
    context = {
        'loan': loan,
        'has_borrowed_items': has_borrowed_items,
    }
    
    return render(request, 'dashboard/loans/detail.html', context)

@login_required
@staff_member_required
def dashboard_return_loan_view(request, loan_id):
    """
    Process batch return/lost with immediate fine payment.
    Handles multiple books at once with damage/lost information.
    """
    loan = get_object_or_404(
        Loan.objects.select_related('user').prefetch_related(
            'loan_items__book'
        ),
        id=loan_id
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
                
                # Check if at least one action is selected (not skip)
                has_action = False
                for item in borrowed_items:
                    action = request.POST.get(f'action_{item.id}')
                    if action and action != 'skip':
                        has_action = True
                        break
                
                if not has_action:
                    messages.warning(request, 'กรุณาเลือกการดำเนินการอย่างน้อย 1 รายการ (คืน หรือ หาย)')
                    return redirect('loans:dashboard_loan_detail', loan_id=loan.id)
                
                for item in borrowed_items:
                    action = request.POST.get(f'action_{item.id}')
                    
                    # Skip items marked as "skip"
                    if action == 'skip' or not action:
                        continue
                    
                    if action == 'return':
                        # Process return
                        item.status = 'returned'
                        item.returned_at = now
                        item.save()
                        
                        # Increase available quantity
                        item.book.available_quantity += 1
                        item.book.save()
                        
                        returned_count += 1
                        
                        # Get late return fine from form (calculated by JavaScript)
                        late_fine_str = request.POST.get(f'late_fine_{item.id}', '').strip()
                        if late_fine_str:
                            try:
                                late_fine_amount = Decimal(late_fine_str)
                                days_late = (now.date() - loan.due_date.date()).days if loan.due_date else 0
                                Fine.objects.create(
                                    loan_item=item,
                                    type='late_return',
                                    amount=late_fine_amount,
                                    reason=f'คืนช้า {days_late} วัน',
                                    paid_at=now
                                )
                                total_fine_amount += late_fine_amount
                            except (ValueError, TypeError):
                                pass
                        
                        # Check for damage fine
                        is_damaged = request.POST.get(f'damaged_{item.id}') == 'true'
                        if is_damaged:
                            damage_amount_str = request.POST.get(f'damage_amount_{item.id}', '').strip()
                            damage_reason = request.POST.get(f'damage_reason_{item.id}', '')
                            
                            if damage_amount_str:
                                try:
                                    damage_amount = Decimal(damage_amount_str)
                                    if damage_amount > 0:
                                        Fine.objects.create(
                                            loan_item=item,
                                            type='damaged',
                                            amount=damage_amount,
                                            reason=damage_reason,
                                            paid_at=now
                                        )
                                        total_fine_amount += damage_amount
                                except (ValueError, TypeError):
                                    pass
                    
                    elif action == 'lost':
                        # Process lost
                        item.status = 'lost'
                        item.returned_at = now
                        item.save()
                        
                        # Decrease total quantity since book is lost
                        item.book.total_quantity -= 1
                        item.book.save()
                        
                        lost_count += 1
                        
                        # Get lost fine from form (calculated by JavaScript)
                        lost_fine_str = request.POST.get(f'lost_fine_{item.id}', '').strip()
                        if lost_fine_str:
                            try:
                                lost_fine_amount = Decimal(lost_fine_str)
                                Fine.objects.create(
                                    loan_item=item,
                                    type='lost',
                                    amount=lost_fine_amount,
                                    reason=f'ทำหนังสือหาย',
                                    paid_at=now
                                )
                                total_fine_amount += lost_fine_amount
                            except (ValueError, TypeError):
                                pass
                
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
                
                return redirect('loans:dashboard_loan_detail', loan_id=loan.id)
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
            return redirect('loans:dashboard_loan_detail', loan_id=loan.id)
    
    # GET request - should not reach here (handled in template)
    return redirect('loans:dashboard_loan_detail', loan_id=loan.id)
