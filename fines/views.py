from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from .models import Fine


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
    # total_amount = fines_list.aggregate(Sum('amount'))['amount__sum'] or 0
    
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
        # 'total_amount': total_amount,
        'fine_late_return_per_day': settings.FINE_LATE_RETURN_PER_DAY,
        'fine_lost_book': settings.FINE_LOST_BOOK,
    }
    
    return render(request, 'fines/list.html', context)


@login_required
@user_passes_test(is_staff)
def dashboard_fines_view(request):
    """
    Display all fines with filtering and sorting capabilities.
    Admin can search by user, filter by type, and sort results.
    All fines are paid immediately upon creation.
    """
    # Get filter parameters
    search_user = request.GET.get('search_user', '').strip()
    filter_type = request.GET.get('filter_type', '').strip()
    sort_by = request.GET.get('sort_by', '-paid_at')
    
    # Query all fines
    fines = Fine.objects.select_related(
        'loan_item__loan__user',
    )
    
    # Apply user search filter (citizen_id, username, email, full name, phone)
    if search_user:
        from django.db.models import Value, CharField
        from django.db.models.functions import Concat
        
        # Build search filter for user fields
        q_filter = Q()
        q_filter |= Q(loan_item__loan__user__citizen_id__icontains=search_user)
        q_filter |= Q(loan_item__loan__user__username__icontains=search_user)
        q_filter |= Q(loan_item__loan__user__email__icontains=search_user)
        q_filter |= Q(loan_item__loan__user__first_name__icontains=search_user)
        q_filter |= Q(loan_item__loan__user__last_name__icontains=search_user)
        q_filter |= Q(loan_item__loan__user__phone_number__icontains=search_user)
        
        # Annotate full name and add to search
        fines = fines.annotate(
            user_full_name=Concat(
                'loan_item__loan__user__first_name', 
                Value(' '), 
                'loan_item__loan__user__last_name', 
                output_field=CharField()
            )
        ).filter(q_filter | Q(user_full_name__icontains=search_user))
    
    # Apply type filter
    if filter_type:
        fines = fines.filter(type=filter_type)
    
    # Apply sorting
    valid_sort_fields = ['paid_at', '-paid_at', 'amount', '-amount']
    if sort_by in valid_sort_fields:
        fines = fines.order_by(sort_by, '-id')  # Add -id as secondary sort for consistency
    else:
        fines = fines.order_by('-paid_at', '-id')
    
    # Pagination
    paginator = Paginator(fines, 20)  # Show 20 fines per page
    page = request.GET.get('page')
    
    try:
        fines_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        fines_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        fines_page = paginator.page(paginator.num_pages)
    
    context = {
        'fines': fines_page,
        'search_user': search_user,
        'filter_type': filter_type,
        'sort_by': sort_by,
        'type_choices': Fine.TYPE_CHOICES,
    }
    
    return render(request, 'dashboard/fines/list.html', context)
