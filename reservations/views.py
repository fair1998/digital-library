from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
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


@login_required
def cancel_reservation_view(request, batch_id):
    """
    Allow user to cancel their own pending reservation batch.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('reservations:my_reservations')
    
    # Get batch and verify ownership
    batch = get_object_or_404(ReservationBatch, id=batch_id, user=request.user)
    
    # Check if user can cancel
    if not batch.can_be_cancelled_by_user():
        messages.error(
            request,
            f'ไม่สามารถยกเลิกการจอง #{batch.id} ได้ (สถานะ: {batch.get_status_display()})'
        )
        return redirect('reservations:my_reservations')
    
    try:
        with transaction.atomic():
            # Update batch status
            batch.status = 'cancelled'
            batch.save()
            
            # Update all reservation items
            for reservation in batch.reservations.all():
                reservation.status = 'cancelled'
                reservation.save()
            
            messages.success(
                request,
                f'ยกเลิกการจอง #{batch.id} สำเร็จ ({batch.reservations.count()} เล่ม)'
            )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('reservations:my_reservations')
