from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # Member URLs
    path('my-reservations/', views.my_reservations_view, name='my_reservations'),
    path('<int:batch_id>/cancel/', views.cancel_reservation_view, name='cancel_reservation'),
]

# Admin Dashboard URLs (accessed via /dashboard/reservations/)
dashboard_urlpatterns = [
    path('reservations/', views.admin_dashboard_view, name='dashboard_reservations'),
    path('reservations/<int:batch_id>/', views.admin_reservation_detail_view, name='dashboard_reservation_detail'),
    path('reservations/<int:batch_id>/confirm/', views.admin_confirm_reservation_view, name='dashboard_reservations_confirm'),
    path('reservations/<int:batch_id>/confirm-selected/', views.admin_confirm_selected_reservations_view, name='dashboard_reservations_confirm_selected'),
    path('reservations/<int:batch_id>/cancel/', views.admin_cancel_reservation_view, name='dashboard_reservations_cancel'),
]
