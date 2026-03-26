from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list_view, name='book_list'),
    path('<int:book_id>/', views.book_detail_view, name='book_detail'),
    # Cart URLs
    path('cart/', views.view_cart, name='view_cart'),
    path('<int:book_id>/add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
    path('<int:book_id>/remove-from-cart/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/confirm/', views.confirm_cart_view, name='confirm_cart'),
    # Deprecated (kept for backward compatibility)
    path('<int:book_id>/reserve/', views.reserve_book_view, name='reserve_book'),
]
