from django.contrib import admin
from .models import CodeSource, CodeSourceTopic


@admin.register(CodeSourceTopic)
class CodeSourceTopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(CodeSource)
class CodeSourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'language', 'difficulty', 'author', 'views_count', 'copies_count', 'is_featured', 'is_published', 'created_at')
    list_filter = ('topic', 'language', 'difficulty', 'is_featured', 'is_published')
    search_fields = ('title', 'summary', 'description', 'tags', 'file_name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'copies_count', 'created_at', 'updated_at')
