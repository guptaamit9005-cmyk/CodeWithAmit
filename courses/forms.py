from django import forms
from .models import Course, CourseCategory, CourseSection, SectionLink, Lesson, Quiz, QuizQuestion

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
            'github_repo_url',
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
            'github_repo_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username/course-repo (Direct GitHub Repository)'}),
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
        self.fields['price'].required = False
        self.fields['original_price'].required = False
        self.fields['estimated_hours'].required = False
        if not self.instance.pk:
            self.fields['price'].initial = 0
            self.fields['original_price'].initial = 0
            self.fields['estimated_hours'].initial = 10
            self.fields['is_published'].initial = True

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_cat = cleaned_data.get('new_category_name')

        if not category and not new_cat:
            self.add_error('category', 'Please select an existing course category or type a new one.')

        if cleaned_data.get('price') is None:
            cleaned_data['price'] = 0
        if cleaned_data.get('original_price') is None:
            cleaned_data['original_price'] = cleaned_data.get('price', 0)
        if not cleaned_data.get('estimated_hours'):
            cleaned_data['estimated_hours'] = 10

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


class CourseSectionForm(forms.ModelForm):
    class Meta:
        model = CourseSection
        fields = ['title', 'order', 'description', 'github_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Module 1: Foundations & Core Concepts'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Overview of topics and deliverables in this module/section...'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/user/repo/tree/main/module-1 (Section-specific GitHub Link)'}),
        }


class SectionLinkForm(forms.ModelForm):
    class Meta:
        model = SectionLink
        fields = ['title', 'url', 'link_type', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Starter Code Repository, Official Documentation'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/... or https://...'}),
            'link_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '1'}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'course',
            'section',
            'title',
            'order',
            'duration_minutes',
            'video_url',
            'github_url',
            'content',
            'code_snippet',
            'code_language',
            'is_free_preview',
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Introduction to React State & Hooks'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '1'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '25'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/watch?v=... (YouTube video/lecture link)'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/... (Direct lesson code link, file, or commit)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Detailed notes, explanation, links, assignments (Markdown/HTML supported)...'}),
            'code_snippet': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 4, 'placeholder': 'Starter or reference code snippet...'}),
            'code_language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'python, javascript, cpp, java'}),
            'is_free_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section'].required = False
        self.fields['duration_minutes'].required = False
        self.fields['order'].required = False
        self.fields['code_language'].required = False
        self.fields['content'].required = False
        self.fields['section'].empty_label = "-- Optional Section / Module --"
        course_id = self.initial.get('course') or (self.instance.course_id if self.instance.pk else None)
        if course_id:
            self.fields['section'].queryset = CourseSection.objects.filter(course_id=course_id)
        else:
            self.fields['section'].queryset = CourseSection.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('duration_minutes'):
            cleaned_data['duration_minutes'] = 15
        if not cleaned_data.get('code_language'):
            cleaned_data['code_language'] = 'python'
        if not cleaned_data.get('order'):
            course = cleaned_data.get('course')
            if course:
                cleaned_data['order'] = course.lessons.count() + 1
            else:
                cleaned_data['order'] = 1
        return cleaned_data


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
