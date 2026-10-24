from django.contrib import admin
from .models import Roadmap, RoadmapStage, RoadmapTopic, UserRoadmapEnrollment, UserTopicProgress

class RoadmapTopicInline(admin.StackedInline):
    model = RoadmapTopic
    extra = 1

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_role', 'estimated_time', 'website_url', 'order', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'target_role', 'website_url')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(RoadmapStage)
class RoadmapStageAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'level', 'order', 'estimated_stage_time')
    list_filter = ('level', 'roadmap')
    inlines = [RoadmapTopicInline]

@admin.register(RoadmapTopic)
class RoadmapTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'stage', 'order', 'related_course', 'related_question')
    list_filter = ('stage__roadmap', 'stage')

@admin.register(UserRoadmapEnrollment)
class UserRoadmapEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roadmap', 'enrolled_at')

@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'is_completed', 'completed_at')
    list_filter = ('is_completed',)
