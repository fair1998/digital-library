from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    # Member views
    path('my-loans/', views.my_loans_view, name='my_loans'),
    
    # API endpoints
    path('api/search-books/', views.search_books_api, name='search_books_api'),
    
    # Admin views
    path('admin/create/<int:batch_id>/', views.create_loan_view, name='create_loan'),
    path('admin/active/', views.active_loans_view, name='active_loans'),
    path('admin/detail/<int:batch_id>/', views.loan_detail_view, name='loan_detail'),
    path('admin/mark-returned/<int:item_id>/', views.mark_returned_view, name='mark_returned'),
    path('admin/mark-lost/<int:item_id>/', views.mark_lost_view, name='mark_lost'),
]
