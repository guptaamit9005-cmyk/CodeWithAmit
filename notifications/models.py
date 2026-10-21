from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('class', 'Live Class'),
        ('course', 'Course Update'),
        ('note', 'Notes Approved'),
        ('streak', 'Coding Streak'),
        ('system', 'System Announcement'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link_url = models.CharField(max_length=255, blank=True)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({'Read' if self.is_read else 'Unread'})"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
