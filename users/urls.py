from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'), 
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/users/', views.dashboard_users_view, name='dashboard_users'),
    path('dashboard/users/<int:user_id>/', views.dashboard_users_detail_view, name='dashboard_users_detail'),

    path('api/users/<int:user_id>/status/', views.toggle_user_status_api , name='toggle_user_status'),
]