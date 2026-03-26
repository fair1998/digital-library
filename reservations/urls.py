from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    path('my-reservations/', views.my_reservations_view, name='my_reservations'),
]
