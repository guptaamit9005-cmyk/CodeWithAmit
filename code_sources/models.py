from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class CodeSourceTopic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=60, default="bi-folder-symlink", help_text="Bootstrap icon class")
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CodeSource(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('typescript', 'TypeScript'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('sql', 'SQL / PostgreSQL'),
        ('html', 'HTML / CSS'),
        ('bash', 'Bash / Shell'),
        ('go', 'Golang'),
        ('rust', 'Rust'),
        ('json', 'JSON / Config'),
    ]

    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    TOPIC_PRESETS = [
        ('Data Structures & Algorithms', 'Data Structures & Algorithms'),
        ('Full-Stack Web Dev', 'Full-Stack Web Dev'),
        ('Python & Automation', 'Python & Automation'),
        ('Django & REST APIs', 'Django & REST APIs'),
        ('React & Modern Frontend', 'React & Modern Frontend'),
        ('System Design & Architecture', 'System Design & Architecture'),
        ('Databases & SQL Queries', 'Databases & SQL Queries'),
        ('DevOps, Docker & Cloud', 'DevOps, Docker & Cloud'),
        ('Open-Source Boilerplates', 'Open-Source Boilerplates'),
    ]

    title = models.CharField(max_length=255, help_text="e.g. Distributed LRU Cache Engine with O(1) Ops")
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    topic = models.CharField(max_length=100, choices=TOPIC_PRESETS, default='Data Structures & Algorithms', help_text="Topic or domain category")
    language = models.CharField(max_length=40, choices=LANGUAGE_CHOICES, default='python')
    difficulty = models.CharField(max_length=30, choices=DIFFICULTY_CHOICES, default='Intermediate')
    
    summary = models.CharField(max_length=350, help_text="Brief 1-2 sentence overview shown on resource cards")
    description = models.TextField(help_text="Detailed explanation of the code, how to run it, and prerequisites")
    file_name = models.CharField(max_length=100, default='main.py', help_text="e.g. lru_cache.py, App.jsx, solution.cpp")
    code_content = models.TextField(help_text="Full source code snippet")

    # GitHub Repository & Demo links requested by User
    github_repo_url = models.URLField(max_length=500, help_text="Direct link to the GitHub repository or source directory")
    demo_url = models.URLField(max_length=500, blank=True, help_text="Optional live demo URL")

    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags e.g. python, cache, lru, oop")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_sources')

    views_count = models.PositiveIntegerField(default=0)
    copies_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'code-source'
            slug = base_slug
            counter = 1
            while CodeSource.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} [{self.topic}]"

    def get_tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def line_count(self):
        if not self.code_content:
            return 0
        return len(self.code_content.splitlines())
