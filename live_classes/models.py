from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

class LiveClass(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live Now'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_classes')
    
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    
    google_meet_url = models.URLField(help_text="Google Meet meeting link (e.g., https://meet.google.com/abc-defg-hij)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    # Post-class resources
    recording_url = models.URLField(blank=True, help_text="YouTube or Drive link to class recording")
    notes_attachment = models.FileField(upload_to='class_resources/', blank=True, null=True)
    additional_resources = models.TextField(blank=True, help_text="Links and notes shared after class")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date', 'start_time']
        verbose_name_plural = "Live Classes"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while LiveClass.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.scheduled_date} at {self.start_time}"

    @property
    def start_datetime(self):
        return datetime.combine(self.scheduled_date, self.start_time)

    @property
    def end_datetime(self):
        return self.start_datetime + timedelta(minutes=self.duration_minutes)

    @property
    def is_currently_live(self):
        now = timezone.localtime()
        class_start = timezone.make_aware(self.start_datetime) if timezone.is_naive(self.start_datetime) else self.start_datetime
        class_end = class_start + timedelta(minutes=self.duration_minutes)
        # Consider live if between 5 mins before start and end
        return (class_start - timedelta(minutes=5)) <= now <= class_end and self.status != 'cancelled'

    @property
    def attendee_count(self):
        return self.attendees.count()


class ClassAttendee(models.Model):
    live_class = models.ForeignKey(LiveClass, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_classes')
    registered_at = models.DateTimeField(auto_now_add=True)
    has_joined = models.BooleanField(default=False)
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('live_class', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.live_class.title}"
