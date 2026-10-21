from django import forms
from .models import Course, CourseCategory, Lesson, Quiz, QuizQuestion

class CourseCategoryForm(forms.ModelForm):
    class Meta:
        model = CourseCategory
        fields = ['name', 'icon', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full-Stack Web Development'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. bi-code-slash'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category overview...'}),
        }


class CourseForm(forms.ModelForm):
    new_category_name = forms.CharField(
        required=False,
        max_length=100,
        label="Or create new category",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Web Development, Artificial Intelligence, Mobile Dev'
        })
    )

    class Meta:
        model = Course
        fields = [
            'title',
            'batch_name',
            'category',
            'difficulty',
            'tag',
            'price',
            'original_price',
            'batch_start_date',
            'language',
            'prerequisites',
            'estimated_hours',
            'short_description',
            'description',
            'thumbnail_url',
            'thumbnail',
            'is_published',
            'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Delta 5.0: Full Stack Web Development (MERN)'}),
            'batch_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Delta 5.0, Sigma 4.0, Alpha Java'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bestseller 🔥, Trending ⚡, Placement Special'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 4499 (0 for Free)'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8999'}),
            'batch_start_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 25th Oct | New Live Cohort'}),
            'language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hinglish (Hindi + English)'}),
            'prerequisites': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. No prior coding experience required'}),
            'estimated_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '120'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A concise one-line summary of this batch'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed syllabus, topics covered, what students will build...'}),
            'thumbnail_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://images.unsplash.com/... (optional online image)'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_cat = cleaned_data.get('new_category_name')

        if not category and not new_cat:
            self.add_error('category', 'Please select an existing course category or type a new one.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_cat = self.cleaned_data.get('new_category_name')
        if new_cat and new_cat.strip():
            cat_obj, _ = CourseCategory.objects.get_or_create(name=new_cat.strip())
            instance.category = cat_obj

        if commit:
            instance.save()
        return instance


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'course',
            'title',
            'order',
            'duration_minutes',
            'video_url',
            'content',
            'code_snippet',
            'code_language',
            'is_free_preview',
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Introduction to React State & Hooks'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '1'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '25'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=... (YouTube video/lecture link)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Detailed notes, explanation, links, assignments (Markdown/HTML supported)...'}),
            'code_snippet': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 4, 'placeholder': 'Starter or reference code snippet...'}),
            'code_language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'python, javascript, cpp, java'}),
            'is_free_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = [
            'question_text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_option',
            'explanation',
        ]
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter question text...'}),
            'option_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}),
            'correct_option': forms.Select(attrs={'class': 'form-select'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Explanation for correct answer...'}),
        }
