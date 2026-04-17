from django.urls import path
from . import views

app_name = 'fines'

urlpatterns = [
    path('my-fines/', views.my_fines_view, name='my_fines'),

    path('dashboard/fines/', views.dashboard_fines_view, name='dashboard_fines'),
]
