from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.utils import timezone
from books.models import Book
from reservations.models import ReservationBatch
from loans.models import LoanBatch, LoanItem
from fines.models import Fine


@staff_member_required
def dashboard_home_view(request):
    """
    Main admin dashboard showing overview of all system data.
    """
    # Books statistics
    total_books = Book.objects.count()
    total_book_copies = Book.objects.aggregate(total=Count('id'))
    available_books = Book.objects.filter(available_quantity__gt=0).count()
    
    # Reservations statistics
    pending_reservations = ReservationBatch.objects.filter(status='pending').count()
    confirmed_reservations = ReservationBatch.objects.filter(status='confirmed').count()
    expired_reservations = ReservationBatch.objects.filter(
        status='pending',
        expires_at__lt=timezone.now()
    ).count()
    
    # Loans statistics
    active_loans = LoanItem.objects.filter(status='borrowed').count()
    overdue_loans = LoanItem.objects.filter(
        status='borrowed',
        loan_batch__due_date__lt=timezone.now()
    ).count()
    returned_loans = LoanItem.objects.filter(status='returned').count()
    lost_books = LoanItem.objects.filter(status='lost').count()
    
    # Fines statistics
    unpaid_fines = Fine.objects.filter(status='unpaid').count()
    unpaid_fines_amount = Fine.objects.filter(status='unpaid').aggregate(
        total=Count('id')
    )
    total_fines_amount = Fine.objects.aggregate(total=Count('id'))
    
    # Recent activities
    recent_reservations = ReservationBatch.objects.select_related('user').order_by('-created_at')[:5]
    recent_loans = LoanBatch.objects.select_related('user').order_by('-created_at')[:5]
    
    context = {
        # Books
        'total_books': total_books,
        'available_books': available_books,
        
        # Reservations
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'expired_reservations': expired_reservations,
        
        # Loans
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'returned_loans': returned_loans,
        'lost_books': lost_books,
        
        # Fines
        'unpaid_fines': unpaid_fines,
        'unpaid_fines_amount': unpaid_fines_amount.get('total', 0),
        'total_fines_amount': total_fines_amount.get('total', 0),
        
        # Recent activities
        'recent_reservations': recent_reservations,
        'recent_loans': recent_loans,
    }
    
    return render(request, 'dashboard/home.html', context)
