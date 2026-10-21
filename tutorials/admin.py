from django.contrib import admin
from .models import TutorialCategory, TutorialTopic

@admin.register(TutorialCategory)
class TutorialCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'badge_text', 'total_topics')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

@admin.register(TutorialTopic)
class TutorialTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'chapter', 'order', 'read_time', 'is_published', 'views_count')
    list_filter = ('category', 'chapter', 'is_published')
    search_fields = ('title', 'content', 'summary', 'chapter')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('category', 'order')
