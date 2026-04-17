from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import json
from books.models import Book
from holds.models import Hold
from loans.models import Loan, LoanItem
from fines.models import Fine

User = get_user_model()


@staff_member_required
def dashboard_home_view(request):
    """
    Main admin dashboard showing overview of all system data.
    """
    # Books statistics
    total_books = Book.objects.count()
    total_book_copies = Book.objects.aggregate(total=Sum('total_quantity'))['total'] or 0
    available_books = Book.objects.filter(available_quantity__gt=0).count()
    
    # Users statistics
    total_users = User.objects.filter(is_active=True).count()
    total_staff = User.objects.filter(is_staff=True).count()
    
    # Hold items statistics
    pending_hold_items = Hold.objects.filter(status='pending').count()
    confirmed_hold_items = Hold.objects.filter(status='confirmed').count()
    expired_hold_items = Hold.objects.filter(
        status='pending',
        expires_at__lt=timezone.now()
    ).count()
    
    # Loans statistics
    active_loans = LoanItem.objects.filter(status='borrowed').count()
    overdue_loans = LoanItem.objects.filter(
        status='borrowed',
        loan__due_date__lt=timezone.now()
    ).count()
    returned_loans = LoanItem.objects.filter(status='returned').count()
    lost_books = LoanItem.objects.filter(status='lost').count()
    
    # Fines statistics (all fines are paid immediately)
    total_fines = Fine.objects.count()
    total_fines_amount = Fine.objects.aggregate(total=Sum('amount'))['total'] or 0
    unpaid_fines_amount = 0  # All fines are paid immediately in this system
    
    # Monthly loan statistics for charts (last 12 months)
    monthly_loans = []
    monthly_labels = []
    today = timezone.now()
    
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=30*i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if i == 0:
            month_end = today
        else:
            next_month = month_start + timedelta(days=32)
            month_end = next_month.replace(day=1) - timedelta(seconds=1)
        
        count = Loan.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        
        monthly_loans.append(count)
        monthly_labels.append(month_start.strftime('%b %Y'))
    
    # Top borrowed books
    top_borrowed_books = Book.objects.annotate(
        borrow_count=Count('loan_items')
    ).order_by('-borrow_count')[:5]
    
    # Recent activities
    recent_hold_items = Hold.objects.select_related('user').order_by('-created_at')[:5]
    recent_loans = Loan.objects.select_related('user').order_by('-created_at')[:5]
    
    context = {
        # Books
        'total_books': total_books,
        'total_book_copies': total_book_copies,
        'available_books': available_books,
        
        # Users
        'total_users': total_users,
        'total_staff': total_staff,
        
        # Hold items
        'pending_hold_items': pending_hold_items,
        'confirmed_hold_items': confirmed_hold_items,
        'expired_hold_items': expired_hold_items,
        
        # Loans
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'returned_loans': returned_loans,
        'lost_books': lost_books,
        
        # Fines (all paid)
        'total_fines': total_fines,
        'total_fines_amount': total_fines_amount,
        'unpaid_fines_amount': unpaid_fines_amount,
        
        # Charts data
        'monthly_loans': json.dumps(monthly_loans),
        'monthly_labels': json.dumps(monthly_labels),
        'top_borrowed_books': top_borrowed_books,
        
        # Recent activities
        'recent_hold_items': recent_hold_items,
        'recent_loans': recent_loans,
    }
    
    return render(request, 'dashboard/home.html', context)
