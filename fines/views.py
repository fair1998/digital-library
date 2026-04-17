from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Fine
from loans.models import Loan


def is_staff(user):
    """Check if user is staff/admin."""
    return user.is_staff


@login_required
def my_fines_view(request):
    """
    Display user's fine history.
    All fines are paid immediately, so no unpaid/paid distinction.
    """
    fines_list = Fine.objects.filter(
        loan_item__loan__user=request.user
    ).select_related(
        'loan_item__loan'
    ).order_by('-paid_at')
    
    # Calculate total (from all fines, not just current page)
    total_amount = fines_list.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Pagination
    paginator = Paginator(fines_list, 20)  # Show 20 fines per page
    page = request.GET.get('page')
    
    try:
        fines = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        fines = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        fines = paginator.page(paginator.num_pages)
    
    context = {
        'fines': fines,
        'total_amount': total_amount,
    }
    
    return render(request, 'fines/list.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_fines_view(request):
    """
    Display loan batches with fines grouped by batch.
    Admin can search by user or loan batch ID.
    All fines are paid immediately upon creation.
    """
    # Get filter parameters
    search_query = request.GET.get('search', '')
    
    # Query loan batches that have fines
    loans = Loan.objects.filter(
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
        loans = loans.filter(q_filter).distinct()
    
    loans = loans.order_by('-created_at')
    
    # Calculate totals across all fines
    all_fines = Fine.objects.all()
    total_all = all_fines.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'loan_batches': loans,
        'total_all': total_all,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/fines/list.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_fines_detail_view(request, loan_id):
    """
    Display detailed fine information for a specific loan batch.
    All fines are paid immediately upon creation.
    """
    loan_batch = get_object_or_404(
        Loan.objects.select_related('user').prefetch_related(
            'loan_items__book__publisher',
            'loan_items__book__authors',
            'loan_items__fines'
        ),
        id=loan_id
    )
    
    # Get all loan items with fines
    loan_items_with_fines = loan_batch.loan_items.filter(fines__isnull=False).distinct()
    
    # Calculate totals for this batch
    all_fines = Fine.objects.filter(loan_item__loan=loan_batch)
    total_amount = all_fines.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'loan_batch': loan_batch,
        'loan_items_with_fines': loan_items_with_fines,
        'total_amount': total_amount,
    }
    
    return render(request, 'dashboard/fines/detail.html', context)
