from django.contrib import admin
from .models import UserProfile, Badge, UserBadge

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'headline', 'points', 'streak_count', 'last_active_date')
    list_filter = ('role', 'last_active_date')
    search_fields = ('user__username', 'user__email', 'headline', 'target_career')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'color', 'points_reward')
    list_filter = ('category', 'color')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at')
    list_filter = ('badge', 'awarded_at')
