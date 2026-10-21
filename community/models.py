from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class DoubtTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DoubtQuestion(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doubt_questions')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    body = models.TextField(help_text="Explain your doubt, what you tried, and what error you are getting.")
    code_snippet = models.TextField(blank=True, help_text="Relevant code snippet")
    language = models.CharField(max_length=30, default='python', blank=True)
    raw_tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated e.g. python, recursion, dynamic-programming")
    tags = models.ManyToManyField(DoubtTag, related_name='questions', blank=True)
    views_count = models.PositiveIntegerField(default=0)
    upvotes = models.ManyToManyField(User, related_name='doubt_question_upvotes', blank=True)
    has_accepted_answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'doubt'
            slug = base_slug
            counter = 1
            while DoubtQuestion.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def total_upvotes(self):
        return self.upvotes.count()

    @property
    def total_answers(self):
        return self.answers.count()

    def get_tag_list(self):
        if self.raw_tags:
            return [t.strip() for t in self.raw_tags.split(',') if t.strip()]
        return [t.name for t in self.tags.all()]


class DoubtAnswer(models.Model):
    question = models.ForeignKey(DoubtQuestion, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doubt_answers')
    body = models.TextField(help_text="Detailed solution or explanation")
    code_snippet = models.TextField(blank=True, help_text="Code snippet supporting your answer")
    is_accepted = models.BooleanField(default=False)
    upvotes = models.ManyToManyField(User, related_name='doubt_answer_upvotes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_accepted', '-created_at']

    def __str__(self):
        return f"Answer by {self.author.username} on '{self.question.title}'"

    @property
    def total_upvotes(self):
        return self.upvotes.count()
