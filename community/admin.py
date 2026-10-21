from django.contrib import admin
from .models import DoubtTag, DoubtQuestion, DoubtAnswer

@admin.register(DoubtTag)
class DoubtTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DoubtQuestion)
class DoubtQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'language', 'views_count', 'has_accepted_answer', 'created_at')
    list_filter = ('has_accepted_answer', 'language', 'created_at')
    search_fields = ('title', 'body', 'raw_tags')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(DoubtAnswer)
class DoubtAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
