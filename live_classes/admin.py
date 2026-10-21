from django.contrib import admin
from .models import LiveClass, ClassAttendee

class ClassAttendeeInline(admin.TabularInline):
    model = ClassAttendee
    extra = 0
    readonly_fields = ('registered_at', 'joined_at')

@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'scheduled_date', 'start_time', 'duration_minutes', 'status', 'attendee_count')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('title', 'description')
    inlines = [ClassAttendeeInline]

@admin.register(ClassAttendee)
class ClassAttendeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'live_class', 'has_joined', 'registered_at')
    list_filter = ('has_joined',)
