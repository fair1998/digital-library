from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import LoanBatch


@login_required
def my_loans_view(request):
    """
    Display user's loan history.
    """
    loan_batches = LoanBatch.objects.filter(
        user=request.user
    ).prefetch_related(
        'loan_items__book__authors',
        'loan_items__book__publisher'
    ).order_by('-created_at')
    
    # Calculate if loans are overdue
    now = timezone.now()
    for batch in loan_batches:
        batch.is_overdue = batch.due_date and batch.due_date < now if batch.due_date else False
        for item in batch.loan_items.all():
            item.is_overdue = batch.is_overdue and item.status == 'borrowed'
    
    context = {
        'loan_batches': loan_batches,
    }
    
    return render(request, 'loans/my_loans.html', context)
