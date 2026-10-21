from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class PlatformFeature(models.Model):
    CATEGORY_CHOICES = [
        ('coding', 'Coding & Sandbox'),
        ('courses', 'Courses & Batches'),
        ('ai_tools', 'AI & Smart Tools'),
        ('interview', 'Interview & DSA'),
        ('resources', 'Notes & Resources'),
        ('community', 'Community & Live Mentorship'),
        ('roadmaps', 'Career Roadmaps'),
        ('utilities', 'Special Tools & Utilities'),
    ]

    title = models.CharField(max_length=150, help_text="Feature Title, e.g. Online Multi-Language Compiler")
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='coding')
    short_description = models.CharField(max_length=250, help_text="Short 1-2 sentence description for cards")
    detailed_description = models.TextField(blank=True, help_text="Detailed highlights (one per line) or in-depth overview")
    icon = models.CharField(max_length=60, default='bi-stars', help_text="Bootstrap icon class, e.g. bi-code-square, bi-cpu, bi-robot, bi-stars")
    color = models.CharField(max_length=30, default='primary', help_text="Color theme: primary, success, warning, danger, info, purple")
    badge_text = models.CharField(max_length=50, blank=True, help_text="Badge text, e.g. Live, New, AI Powered, Free, Popular")
    
    # Navigation / Access Link
    action_url = models.CharField(max_length=300, help_text="Target URL, e.g. /editor/, /practice/, /courses/ or external https:// link")
    action_button_text = models.CharField(max_length=60, default="Launch Feature", help_text="Button text, e.g. Open Compiler, Start Learning, Access Tool")
    is_external = models.BooleanField(default=False, help_text="Check if URL opens in a new tab")

    # Visibility & ordering
    is_active = models.BooleanField(default=True, help_text="Visible to users")
    is_featured = models.BooleanField(default=False, help_text="Featured on homepage and top carousel")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers appear first)")

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_features')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'feature'
            unique_slug = base_slug
            counter = 1
            while PlatformFeature.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def get_highlights_list(self):
        """Returns list of highlights parsed from newline-separated detailed_description."""
        if not self.detailed_description:
            return []
        lines = [line.strip().lstrip('•-* ') for line in self.detailed_description.split('\n') if line.strip()]
        return lines

    def get_resolved_url(self):
        """Safely resolves Django view names, local paths or external URLs."""
        from django.urls import reverse, NoReverseMatch
        url = (self.action_url or '').strip()
        if not url:
            return '#'
        if url.startswith(('http://', 'https://', '/', '#')):
            return url
        try:
            return reverse(url)
        except NoReverseMatch:
            return url

