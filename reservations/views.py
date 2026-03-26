from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import ReservationBatch, Reservation


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


@staff_member_required
def admin_dashboard_view(request):
    """
    Admin dashboard to manage all reservation batches.
    Shows pending, confirmed, cancelled, and expired reservations.
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset
    reservation_batches = ReservationBatch.objects.select_related(
        'user'
    ).prefetch_related(
        'reservations__book__authors',
        'reservations__book__publisher'
    ).order_by('-created_at')
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        reservation_batches = reservation_batches.filter(status=status_filter)
    
    # Add expiry info to each batch
    now = timezone.now()
    for batch in reservation_batches:
        batch.is_expired = batch.expires_at < now if batch.expires_at else False
    
    # Count stats for dashboard
    stats = {
        'total': ReservationBatch.objects.count(),
        'pending': ReservationBatch.objects.filter(status='pending').count(),
        'confirmed': ReservationBatch.objects.filter(status='confirmed').count(),
        'cancelled': ReservationBatch.objects.filter(status='cancelled').count(),
    }
    
    context = {
        'reservation_batches': reservation_batches,
        'status_filter': status_filter,
        'stats': stats,
    }
    
    return render(request, 'reservations/admin_dashboard.html', context)


@staff_member_required
def admin_confirm_reservation_view(request, batch_id):
    """
    Admin action to confirm a pending reservation batch.
    Updates batch status, reservation items status, and book availability.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard_reservations')
    
    batch = get_object_or_404(ReservationBatch, id=batch_id)
    
    # Check if can be confirmed
    if batch.status != 'pending':
        messages.error(
            request,
            f'ไม่สามารถยืนยันการจอง #{batch.id} ได้ (สถานะ: {batch.get_status_display()})'
        )
        return redirect('dashboard_reservations')
    
    try:
        with transaction.atomic():
            # Check book availability
            insufficient_books = []
            for reservation in batch.reservations.all():
                if reservation.book.available_quantity < 1:
                    insufficient_books.append(reservation.book.title)
            
            if insufficient_books:
                messages.error(
                    request,
                    f'ไม่สามารถยืนยันได้ เนื่องจากหนังสือต่อไปนี้ไม่เพียงพอ: {", ".join(insufficient_books)}'
                )
                return redirect('dashboard_reservations')
            
            # Update batch status
            batch.status = 'confirmed'
            batch.save()
            
            # Update all reservation items and decrease book quantity
            for reservation in batch.reservations.all():
                reservation.status = 'confirmed'
                reservation.save()
                
                # Decrease available quantity
                book = reservation.book
                book.available_quantity -= 1
                book.save()
            
            messages.success(
                request,
                f'ยืนยันการจอง #{batch.id} สำเร็จ (User: {batch.user.username}, {batch.reservations.count()} เล่ม)'
            )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('dashboard_reservations')


@staff_member_required
def admin_cancel_reservation_view(request, batch_id):
    """
    Admin action to cancel a reservation batch.
    Can cancel any batch except those already cancelled.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard_reservations')
    
    batch = get_object_or_404(ReservationBatch, id=batch_id)
    
    # Check if already cancelled
    if batch.status == 'cancelled':
        messages.warning(request, f'การจอง #{batch.id} ถูกยกเลิกไปแล้ว')
        return redirect('dashboard_reservations')
    
    try:
        with transaction.atomic():
            # Store old status for message
            old_status = batch.get_status_display()
            
            # If was confirmed, need to return book quantities
            if batch.status == 'confirmed':
                for reservation in batch.reservations.filter(status='confirmed'):
                    book = reservation.book
                    book.available_quantity += 1
                    book.save()
            
            # Update batch status
            batch.status = 'cancelled'
            batch.save()
            
            # Update all reservation items
            for reservation in batch.reservations.all():
                reservation.status = 'cancelled'
                reservation.save()
            
            messages.success(
                request,
                f'ยกเลิกการจอง #{batch.id} สำเร็จ (สถานะเดิม: {old_status}, User: {batch.user.username})'
            )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('dashboard_reservations')
