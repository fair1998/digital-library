from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list_view, name='book_list'),
    path('<int:book_id>/', views.book_detail_view, name='book_detail'),
]
