from django import forms
from .models import TutorialTopic, TutorialCategory

class TutorialCategoryForm(forms.ModelForm):
    ICON_CHOICES = [
        ('bi-diagram-3', 'DSA / Tree / Graph (bi-diagram-3)'),
        ('bi-code-slash', 'Code Slash / General Coding (bi-code-slash)'),
        ('bi-filetype-py', 'Python (bi-filetype-py)'),
        ('bi-filetype-java', 'Java (bi-filetype-java)'),
        ('bi-cpu', 'C++ / Low-Level / Systems (bi-cpu)'),
        ('bi-database', 'SQL / Databases (bi-database)'),
        ('bi-globe2', 'Web Development / Full-Stack (bi-globe2)'),
        ('bi-filetype-js', 'JavaScript / Frontend (bi-filetype-js)'),
        ('bi-robot', 'AI / Machine Learning (bi-robot)'),
        ('bi-layers', 'System Design / Architecture (bi-layers)'),
        ('bi-terminal', 'DevOps / Linux / Git (bi-terminal)'),
        ('bi-shield-check', 'Cybersecurity / Cryptography (bi-shield-check)'),
        ('bi-phone', 'App Development (bi-phone)'),
    ]

    icon_choice = forms.ChoiceField(
        choices=ICON_CHOICES,
        required=False,
        label="Quick Pick Icon",
        widget=forms.Select(attrs={'class': 'form-select select-icon-helper', 'id': 'quickIconPicker'})
    )

    class Meta:
        model = TutorialCategory
        fields = [
            'name',
            'icon',
            'description',
            'order',
            'badge_text',
            'color_theme',
            'is_featured',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Data Structures & Algorithms, React JS, Python'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control font-monospace', 
                'placeholder': 'bi-diagram-3, bi-code-slash'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Explain what students will learn in this tutorial track...'
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'badge_text': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Interview Track, Beginner Friendly, Top Rated'
            }),
            'color_theme': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color', 
                'title': 'Choose accent theme color'
            }),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TutorialTopicForm(forms.ModelForm):
    new_category_name = forms.CharField(
        required=False,
        max_length=120,
        label="Or Create New Category / Series",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'e.g. Dynamic Programming, System Design, Golang'
        })
    )

    class Meta:
        model = TutorialTopic
        fields = [
            'category',
            'chapter',
            'title',
            'order',
            # DSA & Complexity Badges
            'difficulty',
            'read_time',
            'tags',
            'companies',
            'summary',
            'content',
            # Code snippet & language (Optimal Solution)
            'code_snippet',
            'code_language',
            # Multi-language snippets (for DSA & coding)
            'code_snippet_cpp',
            'code_snippet_java',
            'code_snippet_js',
            # Complexity
            'time_complexity',
            'space_complexity',
            # GFG-Style Multi-Approach Solutions
            'brute_force_code',
            'brute_force_complexity',
            'better_code',
            'better_complexity',
            # Interactive Dry-Run Stepper
            'dry_run_steps',
            # GFG Quick MCQ / Quiz
            'quiz_question',
            'quiz_options',
            'quiz_correct_index',
            'quiz_explanation',
            # Screenshot / Code Image
            'screenshot',
            'screenshot_caption',
            # Additional Architecture / Diagram Image
            'diagram_image',
            'diagram_caption',
            # Interactive Visual Graph (Mermaid.js)
            'mermaid_code',
            # Visual Complexity Chart (Chart.js)
            'chart_title',
            'chart_labels',
            'chart_values',
            # Practice link
            'practice_title',
            'practice_url',
            'is_published',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'chapter': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Arrays & Hashing, Binary Search, Trees & Graphs, OOPs'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Two Sum Problem — Optimal Hash Map Approach'
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'read_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 6 min read'}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Arrays, Hash Map, Two Pointers, FAANG Interview'
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Brief 1-2 sentence core concept takeaway...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 
                'rows': 16, 
                'placeholder': 'Write your tutorial here in simple text or Markdown — no HTML needed!\nUse the toolbar buttons above to easily add code snippets, flowcharts, multi-style alert boxes, headings, and tables.'
            }),
            # Primary Code Snippet
            'code_snippet': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 
                'rows': 7, 
                'placeholder': '# Primary solution (e.g. Python solution)...\ndef twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i'
            }),
            'code_language': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'python, cpp, java, javascript, sql'
            }),
            # Multi-language snippets
            'code_snippet_cpp': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 
                'rows': 6, 
                'placeholder': '// Optional C++ Solution...\nvector<int> twoSum(vector<int>& nums, int target) {\n    unordered_map<int, int> mp;\n    for(int i = 0; i < nums.size(); i++) {\n        if(mp.count(target - nums[i])) return {mp[target - nums[i]], i};\n        mp[nums[i]] = i;\n    }\n    return {};\n}'
            }),
            'code_snippet_java': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 
                'rows': 6, 
                'placeholder': '// Optional Java Solution...\npublic int[] twoSum(int[] nums, int target) {\n    Map<Integer, Integer> map = new HashMap<>();\n    for (int i = 0; i < nums.length; i++) {\n        if (map.containsKey(target - nums[i])) return new int[]{map.get(target - nums[i]), i};\n        map.put(nums[i], i);\n    }\n    return new int[]{};\n}'
            }),
            'code_snippet_js': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 
                'rows': 6, 
                'placeholder': '// Optional JavaScript Solution...\nfunction twoSum(nums, target) {\n    const map = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        if (map.has(target - nums[i])) return [map.get(target - nums[i]), i];\n        map.set(nums[i], i);\n    }\n}'
            }),
            # Tags & Companies
            'tags': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Arrays, Hash Map, Two Pointers, FAANG Interview'
            }),
            'companies': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Google, Amazon, Microsoft, Meta, Flipkart, Adobe'
            }),
            'time_complexity': forms.TextInput(attrs={
                'class': 'form-control font-monospace', 
                'placeholder': 'e.g. O(N) or O(log N)'
            }),
            'space_complexity': forms.TextInput(attrs={
                'class': 'form-control font-monospace', 
                'placeholder': 'e.g. O(N) or O(1)'
            }),
            # GFG Multi-Approach Solutions
            'brute_force_code': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 
                'rows': 5, 
                'placeholder': '// Approach 1: Naive / Brute Force Solution (e.g. O(N^2) Nested Loops)...'
            }),
            'brute_force_complexity': forms.TextInput(attrs={
                'class': 'form-control font-monospace', 
                'placeholder': 'e.g. Time: O(N^2), Space: O(1)'
            }),
            'better_code': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 
                'rows': 5, 
                'placeholder': '// Approach 2: Better Approach (e.g. O(N log N) Sorting + Two Pointers)...'
            }),
            'better_complexity': forms.TextInput(attrs={
                'class': 'form-control font-monospace', 
                'placeholder': 'e.g. Time: O(N log N), Space: O(1)'
            }),
            # Interactive Dry-Run Stepper
            'dry_run_steps': forms.Textarea(attrs={
                'class': 'form-control font-monospace', 
                'rows': 4, 
                'placeholder': 'Step 1: Read i=0, num=2, complement=7. Map is empty -> store seen[2]=0\nStep 2: Read i=1, num=7, complement=2. Found in map at index 0 -> Return [0, 1]!'
            }),
            # GFG End-of-Topic Quiz
            'quiz_question': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. What is the average time complexity of single-pass hash map approach?'
            }),
            'quiz_options': forms.TextInput(attrs={
                'class': 'form-control font-monospace', 
                'placeholder': 'O(1), O(N), O(N log N), O(N^2)'
            }),
            'quiz_correct_index': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'max': 3,
                'placeholder': '1 (index of correct option, 0 to 3)'
            }),
            'quiz_explanation': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'e.g. In a single-pass hash map, each element is looked up and inserted in O(1) average time, giving O(N) overall.'
            }),
            # Screenshot / Image
            'screenshot': forms.ClearableFileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*'
            }),
            'screenshot_caption': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Code Implementation Screenshot / Output Terminal'
            }),
            # Additional Diagram / Architecture Image
            'diagram_image': forms.ClearableFileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*'
            }),
            'diagram_caption': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Algorithm Step-by-Step Flowchart / Memory Layout Diagram'
            }),
            # Interactive Visual Graph (Mermaid.js)
            'mermaid_code': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 5,
                'placeholder': 'graph TD\n    A[Start] --> B[Check Condition]\n    B -- Yes --> C[Process Node]\n    B -- No --> D[End]'
            }),
            # Visual Complexity Chart (Chart.js)
            'chart_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Time Complexity Operations for N=1,000'
            }),
            'chart_labels': forms.TextInput(attrs={
                'class': 'form-control font-monospace',
                'placeholder': 'e.g. Hash Map O(1), Binary Search O(log N), Linear Search O(N), Nested Loop O(N^2)'
            }),
            'chart_values': forms.TextInput(attrs={
                'class': 'form-control font-monospace',
                'placeholder': 'e.g. 1, 10, 1000, 1000000'
            }),
            # Practice Link
            'practice_title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Solve Two Sum on LeetCode #1'
            }),
            'practice_url': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'https://leetcode.com/problems/two-sum/'
            }),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['difficulty'].required = False
        self.fields['difficulty'].initial = 'Beginner'
        self.fields['quiz_correct_index'].required = False
        self.fields['quiz_correct_index'].initial = 0

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_cat = cleaned_data.get('new_category_name')

        if not category and not (new_cat and new_cat.strip()):
            self.add_error('category', 'Please select an existing Tutorial track or enter a new one below.')

        if not cleaned_data.get('difficulty'):
            cleaned_data['difficulty'] = 'Beginner'
        if cleaned_data.get('quiz_correct_index') is None:
            cleaned_data['quiz_correct_index'] = 0

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_cat = self.cleaned_data.get('new_category_name')
        if new_cat and new_cat.strip():
            cat_obj, _ = TutorialCategory.objects.get_or_create(name=new_cat.strip())
            instance.category = cat_obj

        if commit:
            instance.save()
        return instance
