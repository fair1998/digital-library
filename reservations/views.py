from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ReservationBatch


@login_required
def my_reservations_view(request):
    """
    Display user's reservation history.
    """
    reservation_batches = ReservationBatch.objects.filter(
        user=request.user
    ).prefetch_related(
        'reservations__book__authors',
        'reservations__book__publisher'
    ).order_by('-created_at')
    
    context = {
        'reservation_batches': reservation_batches,
    }
    
    return render(request, 'reservations/my_reservations.html', context)
