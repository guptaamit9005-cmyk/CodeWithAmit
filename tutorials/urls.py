from django.urls import path
from . import views

app_name = 'tutorials'

urlpatterns = [
    # Directory & Category Listing
    path('', views.tutorial_list, name='tutorial_list'),

    # Category Management (Admin & Staff)
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<slug:category_slug>/edit/', views.edit_category, name='edit_category'),
    path('categories/<slug:category_slug>/delete/', views.delete_category, name='delete_category'),

    # Topic Management (Admin & Staff)
    path('add/', views.add_topic, name='add_topic'),

    # Interactive AJAX endpoints
    path('toggle-progress/<int:topic_id>/', views.toggle_topic_progress, name='toggle_progress_alt'),
    path('topics/<int:topic_id>/toggle-progress/', views.toggle_topic_progress, name='toggle_progress'),
    path('topics/<int:topic_id>/toggle-bookmark/', views.toggle_topic_bookmark, name='toggle_bookmark'),
    path('topics/<int:topic_id>/feedback/', views.submit_topic_feedback, name='submit_feedback'),
    path('topics/<int:topic_id>/save-note/', views.save_topic_note, name='save_topic_note'),
    path('topics/<int:topic_id>/edit/', views.edit_topic_by_id, name='edit_topic_by_id'),
    path('run-code/', views.run_tutorial_code, name='run_tutorial_code'),

    # Detail & Category Root Views
    path('<slug:category_slug>/', views.tutorial_detail, name='category_root'),
    path('<slug:category_slug>/<slug:topic_slug>/', views.tutorial_detail, name='tutorial_detail'),
    path('<slug:category_slug>/<slug:topic_slug>/edit/', views.edit_topic, name='edit_topic'),
    path('<slug:category_slug>/<slug:topic_slug>/delete/', views.delete_topic, name='delete_topic'),
]
