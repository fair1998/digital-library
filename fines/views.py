from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q
from .models import Fine


def is_staff(user):
    """Check if user is staff/admin."""
    return user.is_staff


@login_required
def my_fines_view(request):
    """
    Display user's fine history.
    """
    fines = Fine.objects.filter(
        loan_item__loan_batch__user=request.user
    ).select_related(
        'loan_item__book__publisher',
        'loan_item__loan_batch'
    ).prefetch_related(
        'loan_item__book__authors'
    ).order_by('-created_at')
    
    # Calculate totals
    total_unpaid = fines.filter(status='unpaid').aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid = fines.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'fines': fines,
        'total_unpaid': total_unpaid,
        'total_paid': total_paid,
    }
    
    return render(request, 'fines/my_fines.html', context)


@login_required
@user_passes_test(is_staff)
def admin_fines_report_view(request):
    """
    Display all fines in the system for admin.
    Admin can filter by status, type, and search by user or book.
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    type_filter = request.GET.get('type', 'all')
    search_query = request.GET.get('search', '')
    
    # Base query
    fines = Fine.objects.select_related(
        'loan_item__book__publisher',
        'loan_item__loan_batch__user'
    ).prefetch_related(
        'loan_item__book__authors'
    )
    
    # Apply filters
    if status_filter and status_filter != 'all':
        fines = fines.filter(status=status_filter)
    
    if type_filter and type_filter != 'all':
        fines = fines.filter(type=type_filter)
    
    if search_query:
        q_filter = Q(loan_item__loan_batch__user__username__icontains=search_query)
        q_filter |= Q(loan_item__loan_batch__user__email__icontains=search_query)
        q_filter |= Q(loan_item__book__title__icontains=search_query)
        # If search query is a number, also search by fine ID
        if search_query.isdigit():
            q_filter |= Q(id=int(search_query))
        fines = fines.filter(q_filter).distinct()
    
    fines = fines.order_by('-created_at')
    
    # Calculate totals
    total_unpaid = fines.filter(status='unpaid').aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid = fines.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    total_all = fines.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'fines': fines,
        'total_unpaid': total_unpaid,
        'total_paid': total_paid,
        'total_all': total_all,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search_query': search_query,
    }
    
    return render(request, 'fines/admin_report.html', context)
