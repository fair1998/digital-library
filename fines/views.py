from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q, Count
from .models import Fine
from loans.models import LoanBatch


def is_staff(user):
    """Check if user is staff/admin."""
    return user.is_staff


@login_required
def my_fines_view(request):
    """
    Display user's fine history.
    All fines are paid immediately, so no unpaid/paid distinction.
    """
    fines = Fine.objects.filter(
        loan_item__loan_batch__user=request.user
    ).select_related(
        'loan_item__book__publisher',
        'loan_item__loan_batch'
    ).prefetch_related(
        'loan_item__book__authors'
    ).order_by('-paid_at')
    
    # Calculate total
    total_amount = fines.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'fines': fines,
        'total_amount': total_amount,
    }
    
    return render(request, 'fines/my_fines.html', context)


@login_required
@user_passes_test(is_staff)
def admin_fines_report_view(request):
    """
    Display loan batches with fines grouped by batch.
    Admin can search by user or loan batch ID.
    All fines are paid immediately upon creation.
    """
    # Get filter parameters
    search_query = request.GET.get('search', '')
    
    # Query loan batches that have fines
    loan_batches = LoanBatch.objects.filter(
        loan_items__fines__isnull=False
    ).select_related(
        'user'
    ).prefetch_related(
        'loan_items__fines'
    ).annotate(
        total_fine_amount=Sum('loan_items__fines__amount'),
        fine_count=Count('loan_items__fines', distinct=True)
    ).distinct()
    
    if search_query:
        q_filter = Q(user__username__icontains=search_query)
        q_filter |= Q(user__email__icontains=search_query)
        # If search query is a number, also search by batch ID
        if search_query.isdigit():
            q_filter |= Q(id=int(search_query))
        loan_batches = loan_batches.filter(q_filter).distinct()
    
    loan_batches = loan_batches.order_by('-created_at')
    
    # Calculate totals across all fines
    all_fines = Fine.objects.all()
    total_all = all_fines.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'loan_batches': loan_batches,
        'total_all': total_all,
        'search_query': search_query,
    }
    
    return render(request, 'fines/admin_report.html', context)


@login_required
@user_passes_test(is_staff)
def loan_batch_fines_detail_view(request, batch_id):
    """
    Display detailed fine information for a specific loan batch.
    All fines are paid immediately upon creation.
    """
    loan_batch = get_object_or_404(
        LoanBatch.objects.select_related('user').prefetch_related(
            'loan_items__book__publisher',
            'loan_items__book__authors',
            'loan_items__fines'
        ),
        id=batch_id
    )
    
    # Get all loan items with fines
    loan_items_with_fines = loan_batch.loan_items.filter(fines__isnull=False).distinct()
    
    # Calculate totals for this batch
    all_fines = Fine.objects.filter(loan_item__loan_batch=loan_batch)
    total_amount = all_fines.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'loan_batch': loan_batch,
        'loan_items_with_fines': loan_items_with_fines,
        'total_amount': total_amount,
    }
    
    return render(request, 'fines/batch_detail.html', context)
