"""
URL configuration for Student Success Hub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from accounts.views import leaderboard_view, admin_login_view, student_login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-login/', admin_login_view, name='admin_login_root'),
    path('student-login/', student_login_view, name='student_login_root'),
    path('admin-dashboard/', RedirectView.as_view(url='/dashboard/admin-analytics/', permanent=False)),
    path('student-dashboard/', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('', include('core.urls')),
    path('tutorials/', include('tutorials.urls')),
    path('coding-practice/', RedirectView.as_view(url='/practice/', permanent=False)),
    path('editor/', RedirectView.as_view(url='/practice/', permanent=False)),
    path('compiler/', RedirectView.as_view(url='/practice/', permanent=False)),
    path('practice/', include('coding_practice.urls')),
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('notes/', include('notes.urls')),
    path('live-classes/', RedirectView.as_view(url='/courses/', permanent=False)),
    path('live-classes-archive/', include('live_classes.urls')),
    path('roadmaps/', include('roadmaps.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('community/', include('community.urls')),
    path('source-code/', include('code_sources.urls')),
    path('code-sources/', RedirectView.as_view(url='/source-code/', permanent=False)),
    path('leaderboard/', leaderboard_view, name='global_leaderboard'),
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
