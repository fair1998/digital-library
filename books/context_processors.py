"""
Context processors for books app.
Makes cart information available to all templates.
"""
from .cart import Cart


def cart_context(request):
    """
    Add cart information to template context.
    """
    cart = Cart(request)
    
    # Count confirmed holds for authenticated users
    confirmed_holds_count = 0
    pending_holds_count = 0
    expired_holds_count = 0
    if request.user.is_authenticated:
        from holds.models import Hold
        from django.utils import timezone
        
        confirmed_holds_count = Hold.objects.filter(
            user=request.user,
            status='confirmed'
        ).count()
        
        # Count pending holds and expired confirmed holds for admin/staff users
        if request.user.is_staff:
            pending_holds_count = Hold.objects.filter(
                status='pending'
            ).count()
            
            # Count expired confirmed holds (high priority)
            expired_holds_count = Hold.objects.filter(
                status='confirmed',
                expires_at__lt=timezone.now()
            ).count()
    
    return {
        'cart_count': cart.count(),
        'confirmed_holds_count': confirmed_holds_count,
        'pending_holds_count': pending_holds_count,
        'expired_holds_count': expired_holds_count,
    }
