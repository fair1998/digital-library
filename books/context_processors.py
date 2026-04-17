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
    if request.user.is_authenticated:
        from holds.models import Hold
        confirmed_holds_count = Hold.objects.filter(
            user=request.user,
            status='confirmed'
        ).count()
    
    return {
        'cart_count': cart.count(),
        'confirmed_holds_count': confirmed_holds_count,
    }
