from django.urls import path
from . import views

app_name = 'code_sources'

urlpatterns = [
    path('', views.code_source_list, name='list'),
    path('add/', views.add_code_source, name='add'),
    path('<slug:slug>/', views.code_source_detail, name='detail'),
    path('<slug:slug>/edit/', views.edit_code_source, name='edit'),
    path('<slug:slug>/delete/', views.delete_code_source, name='delete'),
    path('<slug:slug>/download/', views.download_code, name='download'),
    path('<int:pk>/copy/', views.copy_code_api, name='copy_api'),
]
