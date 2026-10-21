from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class NoteCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='bi-journal-bookmark')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Note Categories"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Note(models.Model):
    SEMESTER_CHOICES = [
        ('all', 'All Semesters / General'),
        ('sem_1', 'Semester 1'),
        ('sem_2', 'Semester 2'),
        ('sem_3', 'Semester 3'),
        ('sem_4', 'Semester 4'),
        ('sem_5', 'Semester 5'),
        ('sem_6', 'Semester 6'),
        ('sem_7', 'Semester 7'),
        ('sem_8', 'Semester 8'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(NoteCategory, on_delete=models.CASCADE, related_name='notes')
    subject = models.CharField(max_length=100, help_text="e.g. Operating Systems, DBMS, Machine Learning")
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, default='all')
    programming_language = models.CharField(max_length=50, blank=True, help_text="e.g. Python, C++, Java, or General")
    description = models.TextField()
    
    file = models.FileField(upload_to='notes_documents/')
    file_size = models.CharField(max_length=50, blank=True, help_text="Formatted size e.g. 2.4 MB")
    file_size_bytes = models.BigIntegerField(default=0)

    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_notes')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    is_approved = models.BooleanField(default=True, help_text="Requires admin approval for public view")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_notes')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    download_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Note.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        if self.file and hasattr(self.file, 'size') and self.file.size:
            self.file_size_bytes = self.file.size
            size_mb = self.file.size / (1024 * 1024)
            if size_mb < 1:
                self.file_size = f"{round(self.file.size / 1024, 1)} KB"
            else:
                self.file_size = f"{round(size_mb, 1)} MB"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.subject})"

    @property
    def is_pdf(self):
        if self.file:
            return self.file.name.lower().endswith('.pdf')
        return False


class NoteBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_bookmarks')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'note')
