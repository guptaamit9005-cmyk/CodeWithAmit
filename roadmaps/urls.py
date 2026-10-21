from django.urls import path
from . import views

app_name = 'roadmaps'

urlpatterns = [
    path('', views.roadmap_list, name='roadmap_list'),
    path('create/', views.create_roadmap, name='create_roadmap'),
    path('add-stage/', views.add_stage, name='add_stage'),
    path('stage/<int:stage_id>/edit/', views.edit_stage, name='edit_stage'),
    path('stage/<int:stage_id>/delete/', views.delete_stage, name='delete_stage'),
    path('add-topic/', views.add_topic, name='add_topic'),
    path('topic/<int:topic_id>/edit/', views.edit_topic, name='edit_topic'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
    path('<slug:slug>/', views.roadmap_detail, name='roadmap_detail'),
    path('<slug:slug>/edit/', views.edit_roadmap, name='edit_roadmap'),
    path('<slug:slug>/delete/', views.delete_roadmap, name='delete_roadmap'),
    path('<slug:slug>/enroll/', views.enroll_roadmap, name='enroll_roadmap'),
    path('<slug:slug>/toggle-topic/<int:topic_id>/', views.toggle_topic_progress, name='toggle_topic_progress'),
]
