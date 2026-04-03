from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import ReservationBatch, Reservation
from books.models import Book


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
    Shows pending, confirmed, completed, cancelled, and expired reservations.
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    batch_id_filter = request.GET.get('batch_id', '').strip()
    user_filter = request.GET.get('user', '').strip()
    
    # Base queryset
    reservation_batches = ReservationBatch.objects.select_related(
        'user'
    ).prefetch_related(
        'reservations__book__authors',
        'reservations__book__publisher'
    ).order_by('-created_at')
    
    # Apply batch ID filter
    if batch_id_filter:
        reservation_batches = reservation_batches.filter(id=batch_id_filter)
    
    # Apply user filter (search by username, first name, or last name)
    if user_filter:
        from django.db.models import Q
        reservation_batches = reservation_batches.filter(
            Q(user__username__icontains=user_filter) |
            Q(user__first_name__icontains=user_filter) |
            Q(user__last_name__icontains=user_filter)
        )
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        reservation_batches = reservation_batches.filter(status=status_filter)
    
    # Add expiry info to each batch and collect expired confirmed batches
    now = timezone.now()
    expired_batches = []
    for batch in reservation_batches:
        batch.is_expired = batch.expires_at < now if batch.expires_at else False
        # Collect only CONFIRMED batches that expired (customer didn't pick up)
        if batch.is_expired and batch.status == 'confirmed':
            expired_batches.append(batch)
    
    # Count stats for dashboard
    stats = {
        'total': ReservationBatch.objects.count(),
        'pending': ReservationBatch.objects.filter(status='pending').count(),
        'confirmed': ReservationBatch.objects.filter(status='confirmed').count(),
        'completed': ReservationBatch.objects.filter(status='completed').count(),
        'expired_pending': len(expired_batches),  # Confirmed ที่หมดอายุแต่ยังไม่ได้จัดการ
        'expired': ReservationBatch.objects.filter(status='expired').count(),  # ที่เปลี่ยน status เป็น expired แล้ว
        'cancelled': ReservationBatch.objects.filter(status='cancelled').count(),
    }
    
    context = {
        'reservation_batches': reservation_batches,
        'status_filter': status_filter,
        'batch_id_filter': batch_id_filter,
        'user_filter': user_filter,
        'stats': stats,
        'expired_batches': expired_batches,
    }
    
    return render(request, 'reservations/admin_dashboard.html', context)


@staff_member_required
def admin_reservation_detail_view(request, batch_id):
    """
    Display detailed view of a reservation batch with ability to manage individual items.
    """
    batch = get_object_or_404(
        ReservationBatch.objects.select_related('user').prefetch_related(
            'reservations__book__authors',
            'reservations__book__publisher'
        ),
        id=batch_id
    )
    
    # Check expiry
    now = timezone.now()
    batch.is_expired = batch.expires_at < now if batch.expires_at else False
    
    # Check stock availability
    has_out_of_stock = False
    has_available_books = False
    for reservation in batch.reservations.all():
        if reservation.book.available_quantity == 0:
            has_out_of_stock = True
        else:
            has_available_books = True
    
    context = {
        'batch': batch,
        'has_out_of_stock': has_out_of_stock,
        'has_available_books': has_available_books,
    }
    
    return render(request, 'reservations/reservation_detail.html', context)


@staff_member_required
def admin_confirm_selected_reservations_view(request, batch_id):
    """
    Admin action to confirm selected reservation items.
    Unselected items will be automatically rejected/cancelled.
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
        return redirect('dashboard_reservation_detail', batch_id=batch_id)
    
    # Get selected reservation IDs
    selected_ids = request.POST.getlist('reservation_ids')
    
    if not selected_ids:
        messages.warning(request, 'กรุณาเลือกหนังสือที่ต้องการยืนยัน')
        return redirect('dashboard_reservation_detail', batch_id=batch_id)
    
    try:
        with transaction.atomic():
            # Get all pending reservations
            all_pending = batch.reservations.filter(status='pending').select_related('book')
            
            # Get selected reservations
            selected_reservations = all_pending.filter(id__in=selected_ids)
            
            # Get unselected reservations (to be rejected)
            unselected_reservations = all_pending.exclude(id__in=selected_ids)
            
            # Check availability for selected books
            insufficient_books = []
            confirmed_count = 0
            
            for reservation in selected_reservations:
                if reservation.book.available_quantity < 1:
                    insufficient_books.append(reservation.book.title)
                else:
                    # Confirm this reservation
                    reservation.status = 'confirmed'
                    reservation.save()
                    
                    # Decrease available quantity
                    book = reservation.book
                    book.available_quantity -= 1
                    book.save()
                    
                    confirmed_count += 1
            
            # Reject all unselected items
            rejected_count = 0
            for reservation in unselected_reservations:
                reservation.status = 'cancelled'
                reservation.save()
                rejected_count += 1
            
            # Update batch status
            has_confirmed = batch.reservations.filter(status='confirmed').exists()
            all_processed = not batch.reservations.filter(status='pending').exists()
            
            if has_confirmed:
                batch.status = 'confirmed'
                # Set expiry time for confirmed reservation (user must pick up books before this time)
                expiry_days = getattr(settings, 'RESERVATION_EXPIRY_DAYS', 3)
                batch.expires_at = timezone.now() + timedelta(days=expiry_days)
                batch.save()
            elif all_processed:
                batch.status = 'cancelled'
                batch.save()
            
            # Build success message
            msg_parts = []
            if confirmed_count > 0:
                msg_parts.append(f'ยืนยัน {confirmed_count} เล่ม')
            if rejected_count > 0:
                msg_parts.append(f'ยกเลิก {rejected_count} เล่ม')
            
            messages.success(
                request,
                f'ดำเนินการสำเร็จ: {", ".join(msg_parts)}'
            )
            
            if insufficient_books:
                messages.warning(
                    request,
                    f'ไม่สามารถยืนยันหนังสือต่อไปนี้ได้ (สต็อคไม่พอ): {", ".join(insufficient_books)}'
                )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('dashboard_reservation_detail', batch_id=batch_id)


@staff_member_required
def admin_confirm_reservation_view(request, batch_id):
    """
    Admin action to confirm a pending reservation batch (all items at once).
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
            # Refresh batch data to get latest status
            batch.refresh_from_db()
            
            # Check book availability (only for pending reservations)
            insufficient_books = []
            pending_reservations = batch.reservations.filter(status='pending').select_related('book')
            
            for reservation in pending_reservations:
                # Refresh to get latest available_quantity
                reservation.book.refresh_from_db()
                if reservation.book.available_quantity < 1:
                    insufficient_books.append(reservation.book.title)
            
            if insufficient_books:
                messages.error(
                    request,
                    f'ไม่สามารถยืนยันได้ เนื่องจากหนังสือต่อไปนี้ไม่เพียงพอ: {", ".join(insufficient_books)}'
                )
                return redirect('dashboard_reservations')
            
            # Count how many can be confirmed
            confirmable_count = pending_reservations.filter(
                book__available_quantity__gt=0
            ).count()
            
            if confirmable_count == 0:
                messages.error(request, 'ไม่มีหนังสือที่สามารถยืนยันได้')
                return redirect('dashboard_reservations')
            
            # Update reservation items and decrease book quantity (only pending items)
            confirmed_count = 0
            for reservation in pending_reservations:
                # Refresh reservation to check current status
                reservation.refresh_from_db()
                
                # Only process if still pending (might have been changed)
                if reservation.status == 'pending' and reservation.book.available_quantity > 0:
                    reservation.status = 'confirmed'
                    reservation.save()
                    
                    # Decrease available quantity
                    book = reservation.book
                    book.refresh_from_db()
                    book.available_quantity -= 1
                    book.save()
                    
                    confirmed_count += 1
            
            # Check if all reservations are now confirmed or cancelled
            all_processed = not batch.reservations.filter(status='pending').exists()
            has_confirmed = batch.reservations.filter(status='confirmed').exists()
            
            # Update batch status
            if has_confirmed:
                # If we have at least one confirmed item, mark batch as confirmed
                batch.status = 'confirmed'
                # Set expiry time for confirmed reservation (user must pick up books before this time)
                expiry_days = getattr(settings, 'RESERVATION_EXPIRY_DAYS', 3)
                batch.expires_at = timezone.now() + timedelta(days=expiry_days)
                batch.save()
            elif all_processed:
                # If all items are cancelled and none confirmed, mark batch as cancelled
                batch.status = 'cancelled'
                batch.save()
            
            messages.success(
                request,
                f'ยืนยันการจอง #{batch.id} สำเร็จ ({confirmed_count} เล่ม, User: {batch.user.username})'
            )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('dashboard_reservations')


@staff_member_required
def admin_cancel_reservation_view(request, batch_id):
    """
    Admin action to cancel a reservation batch.
    If expired, mark as 'expired', otherwise 'cancelled'.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('dashboard_reservations')
    
    batch = get_object_or_404(ReservationBatch, id=batch_id)
    
    # Check if already finalized
    if batch.status in ['cancelled', 'expired', 'completed']:
        messages.warning(request, f'การจอง #{batch.id} ถูกจัดการไปแล้ว (สถานะ: {batch.get_status_display()})')
        return redirect('dashboard_reservations')
    
    # Check if this is an expired cancellation
    is_expired_cancellation = batch.is_expired() and batch.status == 'confirmed'
    
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
            
            # Update batch status based on reason
            if is_expired_cancellation:
                batch.status = 'expired'
                new_status = 'หมดอายุ (ลูกค้าไม่มารับ)'
            else:
                batch.status = 'cancelled'
                new_status = 'ยกเลิก'
            
            batch.save()
            
            messages.success(
                request,
                f'{new_status}การจอง #{batch.id} สำเร็จ (สถานะเดิม: {old_status}, User: {batch.user.username})'
            )
            
    except Exception as e:
        messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect('dashboard_reservations')
