from django.urls import path
from . import views

app_name = 'fines'

urlpatterns = [
    # Member views
    path('', views.my_fines_view, name='my_fines'),
]

dashboard_urlpatterns = [
    # Admin views
    path('fines/', views.admin_fines_report_view, name='admin_report'),
    path('fines/batch/<int:batch_id>/', views.loan_batch_fines_detail_view, name='batch_detail'),
]
