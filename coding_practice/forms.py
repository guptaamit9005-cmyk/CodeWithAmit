from django import forms
from .models import CodingQuestion, ProblemCategory, PracticeSet

class PracticeSetForm(forms.ModelForm):
    class Meta:
        model = PracticeSet
        fields = [
            'title',
            'badge',
            'difficulty',
            'description',
            'icon',
            'banner_gradient',
            'order',
            'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Python Programming Practice Set, 450 DSA Sheet, SQL Mastery'
            }),
            'badge': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Top Tech 450, Bestseller, Placement Special'
            }),
            'difficulty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. All Levels, Beginner to Advanced, Intermediate'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Comprehensive summary of what this practice set covers...'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. bi-lightning-charge-fill, bi-filetype-py, bi-database-fill, bi-code-slash'
            }),
            'banner_gradient': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)'
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CodingQuestionForm(forms.ModelForm):
    new_practice_set_title = forms.CharField(
        required=False,
        max_length=200,
        label="Or create new Practice Set / Course Track",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Python Practice Set, SQL Mastery, DSA Sheet'
        })
    )

    new_category_name = forms.CharField(
        required=False,
        max_length=100,
        label="Or create new Topic / Sub-category",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Dynamic Programming, Recursion, Joins, OOPs'
        })
    )

    class Meta:
        model = CodingQuestion
        fields = [
            'title',
            'practice_set',
            'category',
            'difficulty',
            'platform',
            'youtube_solution_url',
            'leetcode_url',
            'gfg_url',
            'company_tags',
            'description',
            'hints',
            'points',
            'is_daily_challenge',
            'time_complexity',
            'space_complexity',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Two Sum, Reverse Linked List, SQL Join Query'}),
            'practice_set': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'youtube_solution_url': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://www.youtube.com/watch?v=... or https://youtu.be/...'
            }),
            'leetcode_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional: https://leetcode.com/problems/two-sum/'}),
            'gfg_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional: https://geeksforgeeks.org/problems/...'}),
            'company_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amazon, Google, Microsoft, Meta'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief problem summary or key objective...'}),
            'hints': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'One hint per line (optional)'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 100}),
            'time_complexity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. O(n) or O(n log n)'}),
            'space_complexity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. O(1) or O(n)'}),
            'is_daily_challenge': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['practice_set'].required = False
        self.fields['leetcode_url'].required = False
        self.fields['youtube_solution_url'].help_text = "Provide a YouTube video solution link. Users will get a direct clickable link to watch on YouTube."

    def clean(self):
        cleaned_data = super().clean()
        practice_set = cleaned_data.get('practice_set')
        new_set = cleaned_data.get('new_practice_set_title')

        if not practice_set and not new_set:
            # If no practice set selected, fall back to default if exists
            default_set = PracticeSet.objects.first()
            if not default_set:
                self.add_error('practice_set', 'Please select or create a Practice Set for this question.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle new Practice Set creation
        new_set_title = self.cleaned_data.get('new_practice_set_title')
        if new_set_title and new_set_title.strip():
            set_obj, _ = PracticeSet.objects.get_or_create(
                title=new_set_title.strip(),
                defaults={'badge': 'Practice Track'}
            )
            instance.practice_set = set_obj
        elif not instance.practice_set:
            default_set = PracticeSet.objects.first()
            if default_set:
                instance.practice_set = default_set

        # Handle new Topic / Category creation
        new_cat = self.cleaned_data.get('new_category_name')
        if new_cat and new_cat.strip():
            cat_obj, _ = ProblemCategory.objects.get_or_create(name=new_cat.strip())
            instance.category = cat_obj
            
        if commit:
            instance.save()
        return instance
