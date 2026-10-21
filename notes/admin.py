from django.contrib import admin
from .models import NoteCategory, Note, NoteBookmark

@admin.register(NoteCategory)
class NoteCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'semester', 'programming_language', 'uploader', 'is_approved', 'download_count', 'uploaded_at')
    list_filter = ('semester', 'is_approved', 'is_featured', 'category')
    search_fields = ('title', 'subject', 'description', 'programming_language')
    prepopulated_fields = {'slug': ('title',)}
    actions = ['approve_notes']

    def approve_notes(self, request, queryset):
        queryset.update(is_approved=True)
    approve_notes.short_description = "Approve selected notes for public display"
