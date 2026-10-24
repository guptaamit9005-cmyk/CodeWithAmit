from django.contrib import admin
from .models import (
    CourseCategory, Course, CourseSection, SectionLink, Lesson, Quiz,
    QuizQuestion, Enrollment, LessonProgress, CourseReview, CourseBookmark, LessonNote
)

@admin.register(LessonNote)
class LessonNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'timestamp_display', 'created_at')
    list_filter = ('lesson__course',)


class SectionLinkInline(admin.TabularInline):
    model = SectionLink
    extra = 1


class CourseSectionInline(admin.StackedInline):
    model = CourseSection
    extra = 0


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 0
    fields = ('title', 'section', 'order', 'duration_minutes', 'video_url', 'github_url', 'is_free_preview', 'content')


class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 1


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'github_url', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'description', 'course__title')
    inlines = [SectionLinkInline]


@admin.register(SectionLink)
class SectionLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'link_type', 'url', 'order')
    list_filter = ('link_type', 'section__course')
    search_fields = ('title', 'url')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'instructor', 'github_repo_url', 'is_published', 'is_featured', 'created_at')
    list_filter = ('category', 'difficulty', 'is_published', 'is_featured')
    search_fields = ('title', 'description', 'github_repo_url')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseSectionInline, LessonInline]

    def save_model(self, request, obj, form, change):
        if not obj.instructor:
            obj.instructor = request.user
        super().save_model(request, obj, form, change)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'section', 'order', 'duration_minutes', 'github_url', 'is_free_preview')
    list_filter = ('course', 'section', 'is_free_preview')
    search_fields = ('title', 'content', 'github_url')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'passing_score')
    inlines = [QuizQuestionInline]

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'is_completed')
    list_filter = ('is_completed', 'enrolled_at')
    search_fields = ('user__username', 'course__title')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'last_accessed_at')
    list_filter = ('is_completed',)

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating', 'created_at')
    list_filter = ('rating',)
