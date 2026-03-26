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
    return {
        'cart_count': cart.count()
    }
