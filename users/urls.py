from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'), 
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    path('dashboard/users/', views.dashboard_users_view, name='dashboard_users'),
    path('dashboard/users/<int:user_id>/', views.dashboard_user_detail_view, name='dashboard_user_detail'),

    path('api/users/', views.get_users_api, name='api_get_users'),
    path('api/users/<int:user_id>/status/', views.put_user_status_api , name='api_put_user_status'),
]