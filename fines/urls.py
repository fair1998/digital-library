from django.urls import path
from . import views

app_name = 'fines'

urlpatterns = [
    # Member views
    path('my-fines/', views.my_fines_view, name='my_fines'),
    
    # Admin views
    path('fines/', views.admin_fines_report_view, name='admin_report'),
]
