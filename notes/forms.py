from django import forms
from .models import Note, NoteCategory

class NoteUploadForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'category', 'subject', 'semester', 'programming_language', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Complete Operating Systems Handwritten Notes'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Operating Systems / CS301'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'programming_language': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. C / C++ / Python or General'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe topics covered, formulas, university syllabus...'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.ppt,.pptx,.txt'}),
        }
