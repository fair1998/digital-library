from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('my-reservations/', views.my_reservations_view, name='my_reservations'),
    path('<int:batch_id>/cancel/', views.cancel_reservation_view, name='cancel_reservation'),
]
