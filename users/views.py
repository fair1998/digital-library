from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
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
    
    # Annotate with statistics
    users = users.annotate(
        total_reservations=Count('reservation_batches', distinct=True),
        total_loans=Count('loan_batches', distinct=True),
        active_loans=Count(
            'loan_batches__loan_items',
            filter=Q(loan_batches__loan_items__status='borrowed'),
            distinct=True
        )
    )
    
    # Pagination
    paginator = Paginator(users, 15)  # 15 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get additional data for each user in current page
    for user in page_obj:
        # Get total fines (all fines are already paid in this system)
        user.total_fines = Fine.objects.filter(
            loan_item__loan_batch__user=user
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get overdue loans
        user.overdue_loans = LoanItem.objects.filter(
            loan_batch__user=user,
            status='borrowed',
            loan_batch__due_date__lt=timezone.now()
        ).count()
    
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
            'message': f'อัพเดทสถานะของ {user.username} เป็น {"เปิดใช้งาน" if user.is_active else "ปิดใช้งาน"}'
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'ไม่พบผู้ใช้'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)