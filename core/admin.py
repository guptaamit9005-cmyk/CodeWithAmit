from django.contrib import admin
from .models import PlatformFeature

@admin.register(PlatformFeature)
class PlatformFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'badge_text', 'action_url', 'is_active', 'is_featured', 'order', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured', 'color')
    search_fields = ('title', 'short_description', 'detailed_description', 'action_url')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'is_featured', 'order')
