from django import forms
from .models import Roadmap, RoadmapStage, RoadmapTopic

class RoadmapForm(forms.ModelForm):
    ICON_CHOICES = [
        ('bi-globe2', '🌐 Web / Full-Stack (Globe)'),
        ('bi-diagram-3', '🌳 DSA & Algorithms (Diagram)'),
        ('bi-cpu', '💻 C++ / Systems & Embedded (CPU)'),
        ('bi-robot', '🤖 AI & Machine Learning (Robot)'),
        ('bi-phone', '📱 Android & Mobile Development (Phone)'),
        ('bi-cloud-check', '☁️ Cloud & DevOps Architecture (Cloud)'),
        ('bi-shield-check', '🛡️ Cybersecurity & Network Security (Shield)'),
        ('bi-database', '🗄️ Backend Engineering & Databases (Database)'),
        ('bi-code-square', '⚡ General Software Engineering (Code)'),
        ('bi-terminal', '💻 Systems & CLI Tools (Terminal)'),
    ]

    BANNER_CHOICES = [
        ('linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)', 'Royal Blue (Classic Engineering)'),
        ('linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)', 'Electric Violet (Full Stack & Cloud)'),
        ('linear-gradient(135deg, #065f46 0%, #059669 100%)', 'Emerald Green (AI, Data & Python)'),
        ('linear-gradient(135deg, #9a3412 0%, #ea580c 100%)', 'Sunset Blaze (Placements & DSA)'),
        ('linear-gradient(135deg, #831843 0%, #db2777 100%)', 'Rose Magenta (Mobile & Design)'),
        ('linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', 'Obsidian Slate (Systems & DevOps)'),
    ]

    icon = forms.ChoiceField(
        choices=ICON_CHOICES,
        initial='bi-globe2',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    banner_color = forms.ChoiceField(
        choices=BANNER_CHOICES,
        initial='linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Roadmap
        fields = [
            'title',
            'target_role',
            'estimated_time',
            'website_url',
            'website_link_label',
            'icon',
            'banner_color',
            'short_description',
            'description',
            'is_published',
            'order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full-Stack Web Developer Roadmap'}),
            'target_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full-Stack Engineer, SDE-1, DevOps Engineer'}),
            'estimated_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 6-8 Months (Self-Paced)'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://roadmap.sh/... or external roadmap link (Optional)'}),
            'website_link_label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Visit roadmap.sh / Official Guide (Optional)'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief 1-sentence career path overview'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Comprehensive breakdown of skill milestones, technologies, and career trajectory...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RoadmapStageForm(forms.ModelForm):
    class Meta:
        model = RoadmapStage
        fields = [
            'roadmap',
            'title',
            'level',
            'order',
            'estimated_stage_time',
            'description',
        ]
        widgets = {
            'roadmap': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Frontend Mastery & React'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '1'}),
            'estimated_stage_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 4-6 Weeks'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What this stage achieves...'}),
        }


class RoadmapTopicForm(forms.ModelForm):
    class Meta:
        model = RoadmapTopic
        fields = [
            'stage',
            'title',
            'order',
            'description',
            'prerequisites',
            'project_ideas',
            'recommended_resources',
            'related_course',
            'related_note',
            'related_question',
        ]
        widgets = {
            'stage': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Asynchronous JavaScript & Promises'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': '1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key concepts to learn...'}),
            'prerequisites': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Basic JS Syntax, Functions'}),
            'project_ideas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Build a Weather App using Fetch API...'}),
            'recommended_resources': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'MDN Docs, YouTube Lecture...'}),
            'related_course': forms.Select(attrs={'class': 'form-select'}),
            'related_note': forms.Select(attrs={'class': 'form-select'}),
            'related_question': forms.Select(attrs={'class': 'form-select'}),
        }
