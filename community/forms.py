from django import forms
from .models import DoubtQuestion, DoubtAnswer

class DoubtQuestionForm(forms.ModelForm):
    class Meta:
        model = DoubtQuestion
        fields = ['title', 'body', 'code_snippet', 'language', 'raw_tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. How to handle Recursion depth limit in Python DFS?'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe your doubt clearly. What were you trying to achieve? What error did you encounter?'
            }),
            'code_snippet': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 5,
                'placeholder': '# Paste your code snippet here...'
            }),
            'language': forms.Select(
                choices=[
                    ('python', 'Python 3'),
                    ('cpp', 'C++'),
                    ('java', 'Java'),
                    ('javascript', 'JavaScript'),
                    ('general', 'General Query / Concepts')
                ],
                attrs={'class': 'form-select'}
            ),
            'raw_tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. python, dsa, dynamic-programming, arrays'
            })
        }


class DoubtAnswerForm(forms.ModelForm):
    class Meta:
        model = DoubtAnswer
        fields = ['body', 'code_snippet']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your clear, step-by-step solution or answer here...'
            }),
            'code_snippet': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 4,
                'placeholder': '# (Optional) Paste corrected code snippet...'
            })
        }
