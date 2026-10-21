from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class TutorialCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    icon = models.CharField(
        max_length=60, 
        default='bi-code-slash', 
        help_text="Bootstrap icon class e.g. bi-code-slash, bi-diagram-3, bi-cpu, bi-database, bi-filetype-py"
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    badge_text = models.CharField(max_length=50, blank=True, default="Tutorial Track")
    color_theme = models.CharField(
        max_length=30, 
        default='#2563eb', 
        help_text="Hex color or theme accent e.g. #2563eb, #10b981, #f59e0b, #8b5cf6"
    )
    is_featured = models.BooleanField(default=False, help_text="Highlight as featured track on tutorials homepage")

    class Meta:
        verbose_name_plural = "Tutorial Categories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def total_topics(self):
        return self.topics.filter(is_published=True).count()


class TutorialTopic(models.Model):
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    category = models.ForeignKey(TutorialCategory, on_delete=models.CASCADE, related_name='topics')
    chapter = models.CharField(max_length=120, default='Basics', help_text="e.g. Getting Started, Arrays, Control Flow, Dynamic Programming, OOPs")
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    order = models.PositiveIntegerField(default=1, help_text="Sequence order within this tutorial series")
    
    summary = models.TextField(blank=True, help_text="Brief 1-2 sentence topic summary")
    content = models.TextField(help_text="Full tutorial article content (HTML or Markdown supported)")
    
    # Primary Code snippet
    code_snippet = models.TextField(blank=True, help_text="Highlight example code for instant copying and testing")
    code_language = models.CharField(max_length=30, default='python', help_text="e.g. python, cpp, java, sql, javascript, html")
    
    # Multi-language support / Alternative solutions
    code_snippet_cpp = models.TextField(blank=True, help_text="Alternative C++ Solution")
    code_snippet_java = models.TextField(blank=True, help_text="Alternative Java Solution")
    code_snippet_js = models.TextField(blank=True, help_text="Alternative JavaScript Solution")

    # Code Screenshot & Diagrams
    screenshot = models.ImageField(
        upload_to='tutorials/screenshots/', 
        blank=True, 
        null=True, 
        help_text="Upload code screenshot, dry-run diagram, or visual architecture"
    )
    screenshot_caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the screenshot")

    # Additional Visual Diagram / Architecture image
    diagram_image = models.ImageField(
        upload_to='tutorials/diagrams/',
        blank=True,
        null=True,
        help_text="Upload additional visual graph, data structure tree, or architecture diagram"
    )
    diagram_caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the diagram image")

    # Interactive Visual Graph (Mermaid.js)
    mermaid_code = models.TextField(
        blank=True, 
        help_text="Visual flowchart / tree / graph (Mermaid.js syntax, e.g. graph TD, tree, sequence diagram)"
    )

    # Interactive Benchmark & Complexity Chart (Chart.js)
    chart_title = models.CharField(max_length=150, blank=True, help_text="Title for visual chart e.g. 'Time Complexity Comparison'")
    chart_labels = models.CharField(max_length=255, blank=True, help_text="Comma-separated labels e.g. Hash Map O(1), Binary Search O(log N), Linear Search O(N)")
    chart_values = models.CharField(max_length=255, blank=True, help_text="Comma-separated numeric values e.g. 1, 14, 1000")

    # DSA & Complexity Badges
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner')
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags e.g. Array, Two Pointers, Dynamic Programming, LeetCode")
    companies = models.CharField(max_length=255, blank=True, help_text="e.g. Google, Amazon, Microsoft, Meta, Flipkart, Adobe")
    time_complexity = models.CharField(max_length=80, blank=True, help_text="e.g. O(N), O(log N), O(N^2)")
    space_complexity = models.CharField(max_length=80, blank=True, help_text="e.g. O(1), O(N)")

    # GFG-Style Multi-Approach Solutions (Brute Force vs Better vs Optimal)
    brute_force_code = models.TextField(blank=True, help_text="Approach 1: Naive / Brute Force Solution")
    brute_force_complexity = models.CharField(max_length=120, blank=True, help_text="e.g. Time: O(N^2), Space: O(1)")
    better_code = models.TextField(blank=True, help_text="Approach 2: Better / Sub-Optimal Solution")
    better_complexity = models.CharField(max_length=120, blank=True, help_text="e.g. Time: O(N log N), Space: O(1)")

    # Interactive Step-by-Step Algorithm Dry Run (Newline or JSON separated steps)
    dry_run_steps = models.TextField(blank=True, help_text="Newline-separated step descriptions for interactive dry-run stepper")

    # Interactive Quick Quiz / Knowledge Check (GFG End-of-Article MCQ)
    quiz_question = models.CharField(max_length=255, blank=True, help_text="e.g. What is the average time complexity of Hash Map lookup?")
    quiz_options = models.TextField(blank=True, help_text="Comma or newline-separated options e.g. O(1), O(N), O(log N), O(N^2)")
    quiz_correct_index = models.PositiveSmallIntegerField(default=0, help_text="0-based index of correct option (0, 1, 2, or 3)")
    quiz_explanation = models.TextField(blank=True, help_text="Explanation shown immediately upon answering")

    read_time = models.CharField(max_length=30, default="5 min read")
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    
    # Optional practice link
    practice_url = models.URLField(blank=True, help_text="Direct link to related LeetCode/GFG problem")
    practice_title = models.CharField(max_length=200, blank=True, help_text="e.g. Solve Two Sum on LeetCode")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('category', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while TutorialTopic.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} -> {self.chapter} -> {self.title}"

    def get_previous_topic(self):
        return TutorialTopic.objects.filter(
            category=self.category,
            is_published=True,
            order__lt=self.order
        ).order_by('-order').first()

    def get_next_topic(self):
        return TutorialTopic.objects.filter(
            category=self.category,
            is_published=True,
            order__gt=self.order
        ).order_by('order').first()

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class TutorialProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutorial_progress')
    topic = models.ForeignKey(TutorialTopic, on_delete=models.CASCADE, related_name='user_progress')
    is_completed = models.BooleanField(default=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user.username} -> {self.topic.title} (Completed)"


class TutorialBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutorial_bookmarks')
    topic = models.ForeignKey(TutorialTopic, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.topic.title}"


class TutorialFeedback(models.Model):
    topic = models.ForeignKey(TutorialTopic, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tutorial_feedbacks')
    is_helpful = models.BooleanField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        helpful_str = "Helpful" if self.is_helpful else "Not Helpful"
        return f"{self.topic.title} - {helpful_str}"


class TutorialNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutorial_notes')
    topic = models.ForeignKey(TutorialTopic, on_delete=models.CASCADE, related_name='user_notes')
    note_text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"Note by {self.user.username} on {self.topic.title}"

