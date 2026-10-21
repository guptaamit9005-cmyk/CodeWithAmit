from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard_alt'),
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('admin-analytics/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard_alt'),
]
