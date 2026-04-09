from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('my-loans/', views.my_loans_view, name='my_loans'),
    
    path('dashboard/loans/', views.dashboard_loans_view, name='dashboard_loans'),
    path('dashboard/loans/<int:loan_id>/', views.dashboard_loan_detail_view, name='dashboard_loan_detail'),
    path('dashboard/loans/<int:loan_id>/return/', views.dashboard_return_loan_view, name='dashboard_return_loan'),
]

