from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # API endpoints
    path('api/<int:user_id>/status/', views.toggle_user_status_api , name='toggle_user_status'),
]

dashboard_urlpatterns = [
    path('users/', views.admin_users_view, name='dashboard_users'),
]
