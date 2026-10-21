from django.urls import path
from . import views

app_name = 'live_classes'

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('create/', views.create_class, name='create_class'),
    path('<int:pk>/', views.class_detail, name='class_detail'),
    path('<int:pk>/edit/', views.edit_class, name='edit_class'),
    path('<int:pk>/delete/', views.delete_class, name='delete_class'),
    path('<int:pk>/register/', views.register_class, name='register_class'),
    path('<int:pk>/join/', views.join_class, name='join_class'),
]
