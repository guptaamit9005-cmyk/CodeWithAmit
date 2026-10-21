from django.contrib import admin
from .models import (
    PracticeSet,
    ProblemCategory,
    CodingQuestion,
    UserQuestionStatus,
    SubmissionRecord,
    ProblemDiscussion,
    DiscussionComment,
    CodingContest,
    ContestParticipant,
    SavedCodeSnippet
)

@admin.register(PracticeSet)
class PracticeSetAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge', 'difficulty', 'order', 'is_featured', 'created_at')
    list_filter = ('difficulty', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ProblemCategory)
class ProblemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CodingQuestion)
class CodingQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'practice_set', 'category', 'difficulty', 'platform', 'youtube_solution_url', 'points', 'is_daily_challenge')
    list_filter = ('practice_set', 'difficulty', 'platform', 'category', 'is_daily_challenge')
    search_fields = ('title', 'description', 'company_tags', 'leetcode_url', 'youtube_solution_url')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(UserQuestionStatus)
class UserQuestionStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'status', 'attempts_count', 'solved_at', 'is_bookmarked')
    list_filter = ('status', 'is_bookmarked')

@admin.register(SubmissionRecord)
class SubmissionRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'language', 'is_passed', 'submitted_at')
    list_filter = ('language', 'is_passed')

@admin.register(ProblemDiscussion)
class ProblemDiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question', 'author', 'category', 'language', 'created_at')
    list_filter = ('category', 'language')
    search_fields = ('title', 'content')

@admin.register(DiscussionComment)
class DiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'author', 'created_at')

@admin.register(CodingContest)
class CodingContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'duration_minutes', 'prize_xp', 'is_active')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = ('contest', 'user', 'score', 'solved_count', 'rank', 'registered_at')
    list_filter = ('contest',)

@admin.register(SavedCodeSnippet)
class SavedCodeSnippetAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'language', 'created_at', 'updated_at')
    list_filter = ('language', 'created_at')
    search_fields = ('title', 'code', 'user__username')

