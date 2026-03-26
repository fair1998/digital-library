from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Fine


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
