from django.urls import path
from . import views

app_name = 'holds'

urlpatterns = [
    path('my-holds/', views.my_holds_view, name='my_holds'),
    path('my-holds/<int:hold_id>/cancel/', views.cancel_hold_view, name='cancel_hold'),

    path('dashboard/holds/', views.dashboard_holds_view, name='dashboard_holds'),
    path('dashboard/holds/<int:hold_id>/', views.dashboard_hold_detail_view, name='dashboard_hold_detail'),
    path('dashboard/holds/<int:hold_id>/confirm-books/', views.dashboard_confirm_hold_books_view, name='dashboard_confirm_hold_books'),
    path('dashboard/holds/<int:hold_id>/cancel/', views.dashboard_cancel_hold_view, name='dashboard_cancel_hold'),
    path('dashboard/holds/<int:hold_id>/create-loan/', views.dashboard_create_loan_from_hold_view, name='dashboard_create_loan_from_hold'),
]
