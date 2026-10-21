from django.contrib import admin
from .models import CourseCategory, Course, Lesson, Quiz, QuizQuestion, Enrollment, LessonProgress, CourseReview, CourseBookmark, LessonNote

@admin.register(LessonNote)
class LessonNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'timestamp_display', 'created_at')
    list_filter = ('lesson__course',)


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1

class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 2

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'instructor', 'is_published', 'is_featured', 'created_at')
    list_filter = ('category', 'difficulty', 'is_published', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration_minutes', 'is_free_preview')
    list_filter = ('course', 'is_free_preview')
    search_fields = ('title', 'content')

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
