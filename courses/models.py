from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import re

class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='bi-code-slash', help_text="Bootstrap or FontAwesome icon class")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Course Categories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or 'category'
            slug = base_slug
            counter = 1
            while CourseCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_courses')
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner')
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, help_text="External image URL fallback")
    github_repo_url = models.URLField(blank=True, default='', help_text="Direct link to course GitHub repository or source code")
    estimated_hours = models.PositiveIntegerField(default=10, blank=True)
    batch_name = models.CharField(max_length=100, blank=True, default='', help_text="e.g. Delta 5.0, Sigma 4.0, Alpha")
    price = models.PositiveIntegerField(default=0, blank=True, help_text="Discounted Price in ₹ (INR), 0 for Free")
    original_price = models.PositiveIntegerField(default=0, blank=True, help_text="Original Price before discount in ₹ (INR)")
    batch_start_date = models.CharField(max_length=100, default='Starts Soon', blank=True)
    language = models.CharField(max_length=100, default='Hinglish (Hindi + English)', blank=True)
    tag = models.CharField(max_length=50, default='Bestseller', blank=True, help_text="e.g. Bestseller, Trending, Placement Special")
    prerequisites = models.CharField(max_length=255, default='No Prior Coding Experience Required', blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def total_lessons(self):
        return self.lessons.count()

    @property
    def total_sections(self):
        return self.sections.count()

    @property
    def has_github(self):
        return bool(self.github_repo_url and self.github_repo_url.strip())

    @property
    def github_repo_name(self):
        if not self.github_repo_url:
            return ""
        clean = self.github_repo_url.strip().rstrip('/')
        if 'github.com/' in clean:
            return clean.split('github.com/', 1)[1]
        return clean

    @property
    def total_enrollments(self):
        return self.enrollments.count()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def get_progress_for_user(self, user):
        if not user.is_authenticated:
            return 0
        total = self.lessons.count()
        if total == 0:
            return 0
        completed = LessonProgress.objects.filter(
            lesson__course=self,
            user=user,
            is_completed=True
        ).count()
        return int((completed / total) * 100)


class CourseSection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, help_text="Overview of what is covered in this module/section")
    github_url = models.URLField(blank=True, default='', help_text="GitHub folder or code repository for this section")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - Section #{self.order}: {self.title}"

    @property
    def total_lessons(self):
        return self.lessons.count()

    @property
    def total_duration_minutes(self):
        return sum(l.duration_minutes for l in self.lessons.all())

    @property
    def has_github(self):
        return bool(self.github_url and self.github_url.strip())


class SectionLink(models.Model):
    LINK_TYPE_CHOICES = [
        ('github', 'GitHub Repository / Code'),
        ('docs', 'Official Documentation'),
        ('notes', 'Notes & Cheat Sheet'),
        ('download', 'Starter Assets / Files'),
        ('external', 'Reference / Article'),
    ]

    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=200, help_text="Display title for this link")
    url = models.URLField(help_text="Direct target link (https://...)")
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='github')
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.section.title} -> {self.title} ({self.get_link_type_display()})"

    @property
    def icon_class(self):
        icons = {
            'github': 'bi-github',
            'docs': 'bi-book-half',
            'notes': 'bi-file-earmark-text-fill',
            'download': 'bi-download',
            'external': 'bi-box-arrow-up-right',
        }
        return icons.get(self.link_type, 'bi-link-45deg')

    @property
    def badge_class(self):
        badges = {
            'github': 'bg-dark text-white',
            'docs': 'bg-primary-subtle text-primary border border-primary-subtle',
            'notes': 'bg-info-subtle text-info-emphasis border border-info-subtle',
            'download': 'bg-success-subtle text-success border border-success-subtle',
            'external': 'bg-secondary-subtle text-secondary border border-secondary-subtle',
        }
        return badges.get(self.link_type, 'bg-light text-dark')


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    section = models.ForeignKey(CourseSection, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    order = models.PositiveIntegerField(default=1, blank=True)
    duration_minutes = models.PositiveIntegerField(default=15, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube video URL or embed link")
    github_url = models.URLField(blank=True, default='', help_text="Direct GitHub link for this lesson code, commit, or repository")
    content = models.TextField(blank=True, default='', help_text="Detailed lesson content (Markdown / HTML supported)")
    code_snippet = models.TextField(blank=True, help_text="Example code snippet")
    code_language = models.CharField(max_length=30, default='python', blank=True)
    is_free_preview = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('course', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'lesson'
            slug = base_slug
            counter = 1
            while Lesson.objects.filter(course=self.course, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - #{self.order} {self.title}"

    @property
    def youtube_embed_id(self):
        """Extracts YouTube video ID from standard or shortened URLs."""
        if not self.video_url:
            return None
        match = re.search(r'(?:v=|\/|youtu\.be\/|embed\/)([0-9A-Za-z_-]{11})', self.video_url)
        return match.group(1) if match else None

    @property
    def has_github(self):
        return bool(self.github_url and self.github_url.strip())


class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.PositiveIntegerField(default=70, help_text="Passing percentage")

    def __str__(self):
        return f"Quiz: {self.lesson.title}"


class QuizQuestion(models.Model):
    OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=2, choices=OPTION_CHOICES)
    explanation = models.TextField(blank=True, help_text="Explanation shown after quiz attempt")

    def __str__(self):
        return f"Q: {self.question_text[:50]}..."


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.user.username} - {self.lesson.title} ({status})"


class CourseBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_bookmarks')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')


class CourseReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-created_at']


class LessonNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_notes')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='student_notes')
    timestamp_seconds = models.PositiveIntegerField(default=0, help_text="Video playback timestamp in seconds")
    note_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp_seconds', '-created_at']

    def __str__(self):
        return f"Note by {self.user.username} on {self.lesson.title} @ {self.timestamp_display}"

    @property
    def timestamp_display(self):
        mins = self.timestamp_seconds // 60
        secs = self.timestamp_seconds % 60
        return f"{mins:02d}:{secs:02d}"

