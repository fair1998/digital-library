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
def dashboard_loans_view(request):
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
    
    return render(request, 'dashboard/loans/list.html', context)


@login_required
@user_passes_test(is_staff)
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
    
    context = {
        'loan': loan,
    }
    
    return render(request, 'dashboard/loans/detail.html', context)

@login_required
@user_passes_test(is_staff)
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
                
                return redirect('loans:dashboard_loan_detail', loan_id=loan.id)
                
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
            return redirect('loans:dashboard_loan_detail', loan_id=loan.id)
    
    # GET request - should not reach here (handled in template)
    return redirect('loans:dashboard_loan_detail', loan_id=loan.id)
