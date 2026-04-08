from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # Member URLs
    path('my-reservations/', views.my_hold_items_view, name='my_reservations'),
    # Action URLs
    path('<int:batch_id>/cancel/', views.cancel_hold_item_view, name='cancel_reservation'),
]

dashboard_urlpatterns = [
    # Admin URLs
    path('reservations/', views.admin_dashboard_view, name='dashboard_reservations'),
    # Action URLs
    path('reservations/<int:batch_id>/', views.admin_hold_item_detail_view, name='dashboard_reservation_detail'),
    path('reservations/<int:batch_id>/confirm/', views.admin_confirm_hold_item_view, name='dashboard_reservations_confirm'),
    path('reservations/<int:batch_id>/confirm-selected/', views.admin_confirm_selected_hold_items_view, name='dashboard_reservations_confirm_selected'),
    path('reservations/<int:batch_id>/cancel/', views.admin_cancel_hold_item_view, name='dashboard_reservations_cancel'),
]
