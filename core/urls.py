from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.global_search, name='search'),
    path('features/', views.features, name='features'),
    path('features/add/', views.add_feature, name='add_feature'),
    path('features/<int:pk>/edit/', views.edit_feature, name='edit_feature'),
    path('features/<int:pk>/delete/', views.delete_feature, name='delete_feature'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
]

