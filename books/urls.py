from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('books/', views.book_list_view, name='book_list'),
    path('books/<int:book_id>/', views.book_detail_view, name='book_detail'),
    # Cart URLs
    path('books/cart/', views.view_cart, name='view_cart'),
    path('books/<int:book_id>/add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
    path('books/<int:book_id>/remove-from-cart/', views.remove_from_cart_view, name='remove_from_cart'),
    path('books/cart/confirm/', views.confirm_cart_view, name='confirm_cart'),
    # Deprecated (kept for backward compatibility)
    path('books/<int:book_id>/reserve/', views.reserve_book_view, name='reserve_book'),

     # Admin
    path('dashboard/books/', views.dashboard_books_view, name='dashboard_books'),
    path('dashboard/books/form/', views.dashboard_book_form_view, name='dashboard_book_form'),
    path('dashboard/books/form/<int:book_id>/', views.dashboard_books_form_id_view, name='dashboard_book_form_id'),
    path('dashboard/books/delete/<int:book_id>/', views.dashboard_book_delete_view, name='dashboard_book_delete'),
]
