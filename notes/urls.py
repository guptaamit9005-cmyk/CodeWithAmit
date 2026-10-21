from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.note_list, name='note_list'),
    path('upload/', views.upload_note, name='upload_note'),
    path('<slug:slug>/', views.note_detail, name='note_detail'),
    path('<slug:slug>/edit/', views.edit_note, name='edit_note'),
    path('<slug:slug>/delete/', views.delete_note, name='delete_note'),
    path('<slug:slug>/download/', views.download_note, name='download_note'),
    path('<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
]
