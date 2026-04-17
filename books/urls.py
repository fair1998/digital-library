from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('books/', views.book_list_view, name='book_list'),
    path('books/<int:book_id>/', views.book_detail_view, name='book_detail'),

    path('books/cart/', views.view_cart, name='view_cart'),
    path('books/<int:book_id>/add-to-cart/', views.add_to_cart_view, name='add_to_cart'),
    path('books/<int:book_id>/remove-from-cart/', views.remove_from_cart_view, name='remove_from_cart'),
    path('books/cart/confirm/', views.confirm_cart_view, name='confirm_cart'),

    path('books/<int:book_id>/reserve/', views.reserve_book_view, name='reserve_book'),

    path('dashboard/books/', views.dashboard_books_view, name='dashboard_books'),
    path('dashboard/books/<int:book_id>/', views.dashboard_book_detail_view, name='dashboard_book_detail'),
    path('dashboard/books/form/', views.dashboard_book_form_view, name='dashboard_book_form'),
    path('dashboard/books/form/<int:book_id>/', views.dashboard_books_form_id_view, name='dashboard_book_form_id'),
    path('dashboard/books/delete/<int:book_id>/', views.dashboard_book_delete_view, name='dashboard_book_delete'),

    path('dashboard/authors/', views.dashboard_authors_view, name='dashboard_authors'),
    path('dashboard/authors/form/', views.dashboard_author_form_view, name='dashboard_author_form'),
    path('dashboard/authors/form/<int:author_id>/', views.dashboard_author_form_id_view, name='dashboard_author_form_id'),
    path('dashboard/authors/delete/<int:author_id>/', views.dashboard_author_delete_view, name='dashboard_author_delete'),

    path('dashboard/categories/', views.dashboard_categories_view, name='dashboard_categories'),
    path('dashboard/categories/form/', views.dashboard_category_form_view, name='dashboard_category_form'),
    path('dashboard/categories/form/<int:category_id>/', views.dashboard_category_form_id_view, name='dashboard_category_form_id'),
    path('dashboard/categories/delete/<int:category_id>/', views.dashboard_category_delete_view, name='dashboard_category_delete'),

    path('dashboard/publishers/', views.dashboard_publishers_view, name='dashboard_publishers'),
    path('dashboard/publishers/form/', views.dashboard_publisher_form_view, name='dashboard_publisher_form'),
    path('dashboard/publishers/form/<int:publisher_id>/', views.dashboard_publisher_form_id_view, name='dashboard_publisher_form_id'),
    path('dashboard/publishers/delete/<int:publisher_id>/', views.dashboard_publisher_delete_view, name='dashboard_publisher_delete'),

    path('api/books/', views.get_books_api, name='get_books'),
    path('api/authors/create/', views.api_create_author, name='api_create_author'),
    path('api/categories/create/', views.api_create_category, name='api_create_category'),
    path('api/publishers/create/', views.api_create_publisher, name='api_create_publisher'),
]
