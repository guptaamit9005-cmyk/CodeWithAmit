from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from courses.models import Course
from notes.models import Note
from coding_practice.models import CodingQuestion

class Roadmap(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='bi-map')
    banner_color = models.CharField(max_length=50, default='linear-gradient(135deg, #0d6efd, #0dcaf0)')
    target_role = models.CharField(max_length=150, help_text="e.g. Full-Stack Web Developer")
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    estimated_time = models.CharField(max_length=100, default='6-8 Months (Estimated)', help_text="Estimated learning duration (clearly labeled)")
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def total_topics(self):
        return RoadmapTopic.objects.filter(stage__roadmap=self).count()

    def get_user_completion_percent(self, user):
        if not user.is_authenticated:
            return 0
        total = self.total_topics
        if total == 0:
            return 0
        completed = UserTopicProgress.objects.filter(
            topic__stage__roadmap=self,
            user=user,
            is_completed=True
        ).count()
        return int((completed / total) * 100)


class RoadmapStage(models.Model):
    STAGE_LEVELS = [
        ('Beginner', 'Beginner Stage'),
        ('Intermediate', 'Intermediate Stage'),
        ('Advanced', 'Advanced Stage'),
    ]

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField(max_length=150)
    level = models.CharField(max_length=20, choices=STAGE_LEVELS, default='Beginner')
    order = models.PositiveIntegerField(default=1)
    estimated_stage_time = models.CharField(max_length=80, blank=True, help_text="e.g. 4-6 Weeks (Estimated)")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.roadmap.title} - {self.title} ({self.level})"


class RoadmapTopic(models.Model):
    stage = models.ForeignKey(RoadmapStage, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    prerequisites = models.CharField(max_length=255, blank=True, help_text="e.g. Basic Loops, Variables")
    project_ideas = models.TextField(blank=True, help_text="Hands-on project ideas for this topic")
    recommended_resources = models.TextField(blank=True, help_text="Curated external links and reading")

    # Platform cross-links
    related_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='roadmap_topics')
    related_note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True, related_name='roadmap_topics')
    related_question = models.ForeignKey(CodingQuestion, on_delete=models.SET_NULL, null=True, blank=True, related_name='roadmap_topics')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.stage.roadmap.title} > {self.title}"

    def is_completed_by_user(self, user):
        if not user.is_authenticated:
            return False
        return UserTopicProgress.objects.filter(user=user, topic=self, is_completed=True).exists()


class UserRoadmapEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmap_enrollments')
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='enrolled_users')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'roadmap')


class UserTopicProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topic_progress')
    topic = models.ForeignKey(RoadmapTopic, on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user.username} - {self.topic.title} ({'Done' if self.is_completed else 'Pending'})"
