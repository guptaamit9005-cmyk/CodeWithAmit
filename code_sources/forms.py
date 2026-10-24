from django import forms
from .models import CodeSource


class CodeSourceForm(forms.ModelForm):
    class Meta:
        model = CodeSource
        fields = [
            'title',
            'topic',
            'language',
            'difficulty',
            'summary',
            'file_name',
            'github_repo_url',
            'demo_url',
            'tags',
            'description',
            'code_content',
            'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. Distributed LRU Cache Engine with O(1) Operations',
                'required': True,
            }),
            'topic': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'language': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-select',
            }),
            'summary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Concise 1-2 sentence overview shown on resource cards...',
                'required': True,
            }),
            'file_name': forms.TextInput(attrs={
                'class': 'form-control font-monospace',
                'placeholder': 'e.g. lru_cache.py, App.jsx, solution.cpp',
            }),
            'github_repo_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/your-username/repository-name',
                'required': True,
            }),
            'demo_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://your-demo-url.vercel.app (optional)',
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'python, dsa, lru-cache, algorithms (comma separated)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Explain what this code does, requirements, how to set it up, run commands, and sample output...',
                'required': True,
            }),
            'code_content': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 16,
                'placeholder': 'Paste complete source code here...',
                'style': 'tab-size: 4; font-size: 0.9rem; line-height: 1.5;',
                'required': True,
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
