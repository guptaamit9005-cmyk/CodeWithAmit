from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

class PracticeSet(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=60, default='bi-lightning-charge-fill', help_text="Bootstrap icon class e.g. bi-lightning-charge-fill, bi-filetype-py, bi-database-fill, bi-code-slash")
    badge = models.CharField(max_length=60, default='Curated Track', blank=True, help_text="e.g. 450 Sheet, Core Subject, Placement Special")
    difficulty = models.CharField(max_length=50, default='All Levels', blank=True)
    banner_gradient = models.CharField(
        max_length=150,
        default='linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
        blank=True
    )
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Practice Set"
        verbose_name_plural = "Practice Sets"
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while PracticeSet.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()

    def get_user_progress(self, user):
        total = self.questions.count()
        if not user.is_authenticated or total == 0:
            return {'total': total, 'solved': 0, 'percent': 0}
        solved_count = UserQuestionStatus.objects.filter(
            user=user,
            question__practice_set=self,
            status='solved'
        ).count()
        percent = int((solved_count / total) * 100) if total > 0 else 0
        return {'total': total, 'solved': solved_count, 'percent': percent}


class ProblemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='bi-cpu')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Problem Categories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CodingQuestion(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    PLATFORM_CHOICES = [
        ('LeetCode', 'LeetCode'),
        ('GeeksforGeeks', 'GeeksforGeeks'),
        ('HackerRank', 'HackerRank'),
        ('CodeStudio', 'CodeStudio'),
        ('Custom', 'Custom / Codestyle'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    practice_set = models.ForeignKey(PracticeSet, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    category = models.ForeignKey(ProblemCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='Easy')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='LeetCode')
    company_tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated e.g. Amazon, Google, Microsoft, Meta")
    youtube_solution_url = models.URLField(max_length=500, blank=True, help_text="YouTube video solution link (External link only)")
    
    # Question details
    description = models.TextField(blank=True, default="Solve this algorithmic challenge. Click 'Solve on LeetCode' to read the full problem description and submit to the online judge.")
    input_format = models.TextField(blank=True)
    output_format = models.TextField(blank=True)
    constraints = models.TextField(blank=True)
    
    # Examples
    example_1_input = models.TextField(blank=True, default="")
    example_1_output = models.TextField(blank=True, default="")
    example_1_explanation = models.TextField(blank=True)
    
    example_2_input = models.TextField(blank=True)
    example_2_output = models.TextField(blank=True)
    example_2_explanation = models.TextField(blank=True)
    
    # Hints (newline or JSON separated)
    hints = models.TextField(blank=True, help_text="One hint per line or markdown")
    
    # External Links
    leetcode_url = models.URLField(blank=True, help_text="Direct link to LeetCode problem")
    gfg_url = models.URLField(blank=True, help_text="Direct link to GeeksforGeeks problem")
    hackerrank_url = models.URLField(blank=True)
    
    # Starter Code Templates
    starter_code_python = models.TextField(blank=True)
    starter_code_cpp = models.TextField(blank=True)
    starter_code_java = models.TextField(blank=True)
    
    # Official Solutions (Editorials)
    solution_python = models.TextField(blank=True)
    solution_cpp = models.TextField(blank=True)
    solution_java = models.TextField(blank=True)
    editorial_explanation = models.TextField(blank=True)
    time_complexity = models.CharField(max_length=100, blank=True, help_text="e.g. O(n log n)")
    space_complexity = models.CharField(max_length=100, blank=True, help_text="e.g. O(1)")

    # Metadata
    is_daily_challenge = models.BooleanField(default=False)
    acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=65.0)
    points = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while CodingQuestion.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.id} {self.title} ({self.difficulty})"

    def get_hints_list(self):
        if not self.hints:
            return []
        return [h.strip() for h in self.hints.split('\n') if h.strip()]

    def get_company_tags_list(self):
        if not self.company_tags:
            return []
        return [tag.strip() for tag in self.company_tags.split(',') if tag.strip()]

    def get_solve_url(self):
        """Returns the primary solve URL, prioritizing leetcode_url."""
        if self.leetcode_url:
            return self.leetcode_url
        if self.gfg_url:
            return self.gfg_url
        if self.hackerrank_url:
            return self.hackerrank_url
        return None

    def get_user_status(self, user):
        if not user.is_authenticated:
            return None
        return self.user_statuses.filter(user=user).first()


class UserQuestionStatus(models.Model):
    STATUS_CHOICES = [
        ('unattempted', 'Unattempted'),
        ('attempted', 'Attempted'),
        ('solved', 'Solved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_statuses')
    question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE, related_name='user_statuses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unattempted')
    is_bookmarked = models.BooleanField(default=False)
    
    # Saved code
    user_code = models.TextField(blank=True)
    selected_language = models.CharField(max_length=20, default='python')
    
    attempts_count = models.PositiveIntegerField(default=0)
    solved_at = models.DateTimeField(null=True, blank=True)
    last_attempted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'question')
        verbose_name_plural = "User Question Statuses"

    def __str__(self):
        return f"{self.user.username} - {self.question.title} ({self.status})"


class SubmissionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coding_submissions')
    question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE, related_name='submissions')
    language = models.CharField(max_length=20)
    code = models.TextField()
    is_passed = models.BooleanField(default=True)
    output_message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']


class ProblemDiscussion(models.Model):
    CATEGORY_CHOICES = [
        ('solution', '💡 Full Solution & Code'),
        ('approach', '🧠 Intuition & Approach'),
        ('optimization', '⚡ Time/Space Optimization'),
        ('doubt', '❓ Doubt / Edge Cases'),
    ]

    question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE, related_name='discussions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coding_discussions')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='solution')
    language = models.CharField(max_length=30, default='python', blank=True)
    content = models.TextField(help_text="Detailed explanation of your logic")
    code_snippet = models.TextField(blank=True, help_text="Paste your clean solution code here")
    youtube_url = models.URLField(max_length=500, blank=True, help_text="YouTube video solution/walkthrough link")
    upvotes = models.ManyToManyField(User, related_name='discussion_upvotes', blank=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    @property
    def total_upvotes(self):
        return self.upvotes.count()

    @property
    def total_comments(self):
        return self.comments.count()


class DiscussionComment(models.Model):
    discussion = models.ForeignKey(ProblemDiscussion, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.discussion.title}"


class CodingContest(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    badge_label = models.CharField(max_length=50, default='Weekly Contest', help_text="e.g. Weekly Contest 42, Biweekly Sprint")
    banner_gradient = models.CharField(max_length=100, default='linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=90)
    questions = models.ManyToManyField(CodingQuestion, related_name='contests', blank=True)
    prize_xp = models.PositiveIntegerField(default=500, help_text="Bonus XP for top finishers")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_live(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def is_upcoming(self):
        return timezone.now() < self.start_time

    @property
    def is_past(self):
        return timezone.now() > self.end_time

    @property
    def total_participants(self):
        return self.participants.count()


class ContestParticipant(models.Model):
    contest = models.ForeignKey(CodingContest, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contest_entries')
    registered_at = models.DateTimeField(auto_now_add=True)
    score = models.PositiveIntegerField(default=0)
    solved_count = models.PositiveIntegerField(default=0)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('contest', 'user')
        ordering = ['-score', 'time_taken_seconds', 'registered_at']

    def __str__(self):
        return f"{self.user.username} - {self.contest.title} (Score: {self.score})"


class SavedCodeSnippet(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python 3'),
        ('c', 'C (GCC)'),
        ('cpp', 'C++ (G++)'),
        ('html', 'HTML / CSS / JS (Web Sandbox)'),
        ('javascript', 'JavaScript (Node.js)'),
        ('css', 'CSS Stylesheet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_snippets', null=True, blank=True)
    title = models.CharField(max_length=200, default='Untitled Snippet')
    language = models.CharField(max_length=30, choices=LANGUAGE_CHOICES, default='python')
    code = models.TextField(blank=True, default='')
    html_code = models.TextField(blank=True, default='')
    css_code = models.TextField(blank=True, default='')
    js_code = models.TextField(blank=True, default='')
    stdin_input = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        author = self.user.username if self.user else "Anonymous"
        return f"{self.title} ({self.get_language_display()}) by {author}"


