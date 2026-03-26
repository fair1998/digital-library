from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('my-loans/', views.my_loans_view, name='my_loans'),
]
