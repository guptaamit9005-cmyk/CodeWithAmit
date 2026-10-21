from django import forms
from .models import LiveClass

class LiveClassScheduleForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ['title', 'description', 'scheduled_date', 'start_time', 'duration_minutes', 'google_meet_url', 'recording_url', 'notes_attachment', 'additional_resources']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Masterclass: Dynamic Programming Patterns'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Class agenda, topics, prerequisites...'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '60'}),
            'google_meet_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/abc-defg-hij'}),
            'recording_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/watch?v=... (Optional)'}),
            'notes_attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'additional_resources': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Shared GitHub repos, notes, slides...'}),
        }
