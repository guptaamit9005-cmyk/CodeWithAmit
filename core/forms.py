from django import forms
from .models import PlatformFeature

class PlatformFeatureForm(forms.ModelForm):
    class Meta:
        model = PlatformFeature
        fields = [
            'title',
            'category',
            'short_description',
            'detailed_description',
            'icon',
            'color',
            'badge_text',
            'action_url',
            'action_button_text',
            'is_external',
            'is_active',
            'is_featured',
            'order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. AI Mock Interviewer, Web3 Sandbox, System Design Lab'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Short 1-2 sentence description for feature cards'
            }),
            'detailed_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter key feature highlights (one per line, e.g.:\n- Real-time AI feedback\n- Over 50+ interview scenarios\n- Instant score and transcript)'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. bi-cpu, bi-code-square, bi-robot, bi-stars, bi-terminal'
            }),
            'color': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('primary', 'Primary (Indigo Blue)'),
                ('success', 'Success (Emerald Green)'),
                ('warning', 'Warning (Amber Yellow)'),
                ('danger', 'Danger (Rose Red)'),
                ('info', 'Info (Sky Cyan)'),
                ('purple', 'Purple (Violet)'),
            ]),
            'badge_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Live, New, AI Powered, Pro, Free, Popular'
            }),
            'action_url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target URL, e.g. /editor/, /practice/, /courses/ or external https:// link'
            }),
            'action_button_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Launch Sandbox, Start Practice, Open Tool'
            }),
            'is_external': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }
