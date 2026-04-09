from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum
from .forms import UserRegistrationForm, UserLoginForm

def register_view(request):
    """View for user registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ')
            return redirect('users:login')
        else:
            messages.error(request, 'กรุณาตรวจสอบข้อมูลที่กรอกและลองใหม่อีกครั้ง')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """View for user login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'ยินดีต้อนรับ {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """View for user logout"""
    logout(request)
    messages.success(request, 'ออกจากระบบสำเร็จ')
    return redirect('home')


def home_view(request):
    """Home page view"""
    return render(request, 'home.html')

@staff_member_required
def dashboard_users_view(request):
    """Admin view to list all users with search, filter, and statistics"""
    from django.contrib.auth import get_user_model
    from django.core.paginator import Paginator
    from django.db.models import Count, Q, Sum
    from django.utils import timezone
    from loans.models import  LoanItem
    from fines.models import Fine
    
    User = get_user_model()
    
    # Get query parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    role_filter = request.GET.get('role', '')
    sort_by = request.GET.get('sort', '-last_login')
    
    # Base queryset
    users = User.objects.all()
    
    # Apply search
    if search_query:
        from django.db.models import Value, CharField
        from django.db.models.functions import Concat
        
        users = users.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField())
        ).filter(
            Q(citizen_id__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Apply role filter
    if role_filter == 'staff':
        users = users.filter(is_staff=True)
    elif role_filter == 'member':
        users = users.filter(is_staff=False)
    
    # Apply status filter
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Apply sorting
    users = users.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(users, 15)  # 15 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Overall statistics
    total_users = User.objects.count()
    total_members = User.objects.filter(is_staff=False).count()
    total_staff = User.objects.filter(is_staff=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'sort_by': sort_by,
        'total_users': total_users,
        'total_members': total_members,
        'total_staff': total_staff,
        'inactive_users': inactive_users,
    }
    
    return render(request, 'dashboard/users/index.html', context)

@staff_member_required
def dashboard_users_detail_view(request, user_id):
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from django.db.models import Count
    from holds.models import Hold, HoldItem
    from loans.models import Loan, LoanItem
    from fines.models import Fine
    from books.models import Category

    User = get_user_model()
    member = get_object_or_404(User, pk=user_id)

    holds_qs = Hold.objects.filter(user=member)
    hold_items_qs = HoldItem.objects.filter(hold__user=member)
    loans_qs = Loan.objects.filter(user=member)
    loan_items_qs = LoanItem.objects.filter(loan__user=member)
    fines_qs = Fine.objects.filter(loan_item__loan__user=member)

    total_fines_amount = fines_qs.aggregate(total=Sum('amount'))['total'] or 0
    late_return_fines_amount = fines_qs.filter(type='late_return').aggregate(total=Sum('amount'))['total'] or 0
    lost_fines_amount = fines_qs.filter(type='lost').aggregate(total=Sum('amount'))['total'] or 0
    damaged_fines_amount = fines_qs.filter(type='damaged').aggregate(total=Sum('amount'))['total'] or 0

    # Get top 5 categories by loan count
    top_categories = Category.objects.filter(
        books__loan_items__loan__user=member
    ).annotate(
        loan_count=Count('books__loan_items', distinct=True)
    ).order_by('-loan_count')[:5]

    context = {
        'member': member,
        'stats': {
            'total_holds': holds_qs.count(),
            'total_reserved_books': hold_items_qs.count(),
            'pending_holds': holds_qs.filter(status='pending').count(),
            'confirmed_holds': holds_qs.filter(status='confirmed').count(),
            'completed_holds': holds_qs.filter(status='completed').count(),
            'expired_holds': holds_qs.filter(status='expired').count(),
            'cancelled_holds': holds_qs.filter(status='cancelled').count(),
            'total_loans': loans_qs.count(),
            'total_loan_books': loan_items_qs.count(),
            'returned_loan_books': loan_items_qs.filter(status='returned').count(),
            'lost_loan_books': loan_items_qs.filter(status='lost').count(),
            'active_loan_books': loan_items_qs.filter(status='borrowed').count(),
            'total_active_loans': loans_qs.filter(status='active').count(),
            'overdue_loans': loan_items_qs.filter(
                status='borrowed',
                loan__due_date__lt=timezone.now(),
            ).count(),
            'completed_loans': loans_qs.filter(status='completed').count(),
            'total_fines_amount': total_fines_amount,
            'total_fines_count': fines_qs.count(),
            'late_return_fines_amount': late_return_fines_amount,
            'lost_fines_amount': lost_fines_amount,
            'damaged_fines_amount': damaged_fines_amount,
        },
        'can_toggle_status': member != request.user,
        'top_categories': top_categories,
    }

    return render(request, 'dashboard/users/detail.html', context)

@staff_member_required
def toggle_user_status_api(request, user_id):
    """Toggle user active status"""
    from django.contrib.auth import get_user_model
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    User = get_user_model()
    
    try:
        user = User.objects.get(pk=user_id)
        
        # Prevent deactivating yourself
        if user == request.user:
            return JsonResponse({
                'error': 'คุณไม่สามารถเปลี่ยนสถานะของตัวเองได้'
            }, status=400)
        
        # Toggle status
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f'อัพเดทสถานะของ {user.get_username()} เป็น {"เปิดใช้งาน" if user.is_active else "ปิดใช้งาน"}'
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'ไม่พบผู้ใช้'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)