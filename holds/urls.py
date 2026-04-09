from django.urls import path
from . import views

app_name = 'holds'

urlpatterns = [
    path('my-holds/', views.my_holds_view, name='my_holds'),
    path('<int:id>/cancel/', views.cancel_hold_book_action, name='cancel_hold_book'),

    path('dashboard/holds/', views.dashboard_holds_view, name='dashboard_holds'),
    path('dashboard/holds/<int:id>/', views.dashboard_hold_detail_view, name='dashboard_hold_detail'),
    path('dashboard/holds/<int:id>/confirm/', views.dashboard_confirm_hold_action, name='dashboard_confirm_hold'),
    path('dashboard/holds/<int:id>/confirm/books/', views.dashboard_confirm_hold_books_action, name='dashboard_confirm_hold_books'),
    path('dashboard/holds/<int:id>/cancel/', views.dashboard_cancel_hold_action, name='dashboard_cancel_hold'),
]
