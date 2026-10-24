from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from courses.models import Course, CourseCategory
from live_classes.models import LiveClass
from roadmaps.models import Roadmap
from coding_practice.models import CodingQuestion
from notes.models import Note
from tutorials.models import TutorialCategory, TutorialTopic
from .models import PlatformFeature
from .forms import PlatformFeatureForm

def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin'))


def home(request):
    """High-converting, vibrant interactive flagship landing page for Codestyle."""
    flagship_batches = Course.objects.filter(is_published=True).select_related('category', 'instructor').order_by('-is_featured', '-created_at')[:6]
    course_categories = CourseCategory.objects.all()
    curated_dsa_questions = CodingQuestion.objects.all().select_related('category')
    tutorial_tracks = TutorialCategory.objects.all().prefetch_related('topics')[:6]
    free_notes = Note.objects.filter(is_approved=True).select_related('category')[:6]
    popular_roadmaps = Roadmap.objects.filter(is_published=True).prefetch_related('stages')[:4]
    upcoming_classes = LiveClass.objects.filter(status__in=['upcoming', 'live']).order_by('scheduled_date', 'start_time')[:3]

    from django.contrib.auth.models import User
    from coding_practice.models import ProblemCategory

    dsa_categories = ProblemCategory.objects.filter(questions__isnull=False).distinct()
    
    total_users_count = User.objects.count()
    total_questions_count = CodingQuestion.objects.count()
    total_notes_count = Note.objects.filter(is_approved=True).count()
    total_courses_count = Course.objects.filter(is_published=True).count()
    total_classes_count = LiveClass.objects.count()
    total_tutorials_count = TutorialTopic.objects.filter(is_published=True).count()

    stats = {
        'total_learners': total_users_count,
        'practice_problems': total_questions_count,
        'free_notes_count': total_notes_count,
        'total_courses': total_courses_count,
        'live_classes': total_classes_count,
        'total_tutorials': total_tutorials_count,
        'community_rating': '4.9/5',
    }

    feature_pillars = [
        {
            'icon': 'bi-mortarboard-fill',
            'color': 'primary',
            'title': 'Structured Industry Batches',
            'subtitle': 'Comprehensive courses covering full stack engineering, system architecture, databases, and algorithms.'
        },
        {
            'icon': 'bi-lightning-charge-fill',
            'color': 'warning',
            'title': 'Curated 450 DSA Sheet',
            'subtitle': 'Topic-wise problems with test cases, complexity analysis, and split-screen code editor.'
        },
        {
            'icon': 'bi-collection-play-fill',
            'color': 'info',
            'title': 'Course-Wise Practice Sets',
            'subtitle': 'Curated problem sets across Python, DSA, SQL, and Web Dev with YouTube solution video links.'
        },
        {
            'icon': 'bi-signpost-split-fill',
            'color': 'danger',
            'title': 'Guided Career Roadmaps',
            'subtitle': 'Structured role-based roadmaps for Frontend, Backend, Fullstack, and Data Engineering careers.'
        }
    ]

    faqs = [
        {
            'q': 'Is Codestyle free for students?',
            'a': 'Yes! The practice sets, tutorials, curated courses, and career roadmaps are completely free for all learners.'
        },
        {
            'q': 'How do the practice problem sets work?',
            'a': 'You can solve topic-wise practice problems in Python, C++, Java, and SQL with detailed step-by-step solutions, test cases, and video walkthroughs.'
        },
        {
            'q': 'Can I join live classes on Google Meet?',
            'a': 'Yes! Mentors schedule live masterclasses and doubt sessions. You can register with one click from the Live Classes portal and join directly via the Google Meet link.'
        },
        {
            'q': 'Are verified certificates provided upon course completion?',
            'a': 'Yes, students who complete course lessons, capstone projects, and module quizzes receive a verified certificate that can be shared on LinkedIn and added to your resume.'
        },
        {
            'q': 'How does Dark Mode work on Codestyle?',
            'a': 'Click the theme toggle icon in the top navigation bar or the floating toggle at any time to seamlessly switch between obsidian Dark Mode and crisp Light Mode. Your preference is automatically saved.'
        }
    ]

    platform_features = PlatformFeature.objects.filter(is_active=True).order_by('order', '-created_at')[:6]

    context = {
        'flagship_batches': flagship_batches,
        'course_categories': course_categories,
        'curated_dsa_questions': curated_dsa_questions,
        'dsa_categories': dsa_categories,
        'tutorial_tracks': tutorial_tracks,
        'free_notes': free_notes,
        'popular_roadmaps': popular_roadmaps,
        'upcoming_classes': upcoming_classes,
        'platform_features': platform_features,
        'stats': stats,
        'feature_pillars': feature_pillars,
        'faqs': faqs,
        'is_admin': request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser),
    }
    return render(request, 'core/home.html', context)


def global_search(request):
    """Unified cross-platform search across tutorials, questions, courses, notes, and roadmaps."""
    query = request.GET.get('q', '').strip()
    tutorial_results = []
    question_results = []
    course_results = []
    note_results = []
    roadmap_results = []

    if query:
        tutorial_results = TutorialTopic.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(summary__icontains=query) | Q(category__name__icontains=query),
            is_published=True
        ).distinct()[:10]

        question_results = CodingQuestion.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query) | Q(company_tags__icontains=query)
        ).distinct()[:10]

        course_results = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query),
            is_published=True
        ).distinct()[:6]

        note_results = Note.objects.filter(
            Q(title__icontains=query) | Q(subject__icontains=query) | Q(description__icontains=query) | Q(programming_language__icontains=query),
            is_approved=True
        ).distinct()[:6]

        roadmap_results = Roadmap.objects.filter(
            Q(title__icontains=query) | Q(target_role__icontains=query) | Q(description__icontains=query),
            is_published=True
        ).distinct()[:6]

    total_results = len(tutorial_results) + len(question_results) + len(course_results) + len(note_results) + len(roadmap_results)

    context = {
        'query': query,
        'tutorial_results': tutorial_results,
        'question_results': question_results,
        'course_results': course_results,
        'note_results': note_results,
        'roadmap_results': roadmap_results,
        'total_results': total_results,
    }
    return render(request, 'core/search_results.html', context)


def features(request):
    """Dedicated dynamic full-page showcase of all platform features, capabilities and tools."""
    is_admin = is_admin_user(request.user)
    
    # Base Queryset: all features for admin, only active for learners
    features_qs = PlatformFeature.objects.all() if is_admin else PlatformFeature.objects.filter(is_active=True)

    # Category Filtering
    current_category = request.GET.get('category', 'all').strip()
    if current_category and current_category != 'all':
        features_qs = features_qs.filter(category=current_category)

    # Keyword Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        features_qs = features_qs.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(detailed_description__icontains=search_query) |
            Q(badge_text__icontains=search_query)
        )

    # Live platform stats
    total_questions = CodingQuestion.objects.count()
    total_notes = Note.objects.filter(is_approved=True).count()
    total_courses = Course.objects.filter(is_published=True).count()
    total_tutorials = TutorialTopic.objects.filter(is_published=True).count()

    # Category pills with count
    all_features_count = PlatformFeature.objects.count() if is_admin else PlatformFeature.objects.filter(is_active=True).count()
    categories_list = [
        {'key': 'all', 'label': 'All Features', 'count': all_features_count}
    ]
    for key, label in PlatformFeature.CATEGORY_CHOICES:
        count = PlatformFeature.objects.filter(category=key).count() if is_admin else PlatformFeature.objects.filter(category=key, is_active=True).count()
        categories_list.append({
            'key': key,
            'label': label,
            'count': count
        })

    context = {
        'features': features_qs,
        'categories_list': categories_list,
        'current_category': current_category,
        'search_query': search_query,
        'is_admin': is_admin,
        'stats': {
            'problems': total_questions,
            'notes': total_notes,
            'courses': total_courses,
            'tutorials': total_tutorials,
        }
    }
    return render(request, 'core/features.html', context)


@login_required
def add_feature(request):
    """Admin controller to dynamically create a new platform feature."""
    if not is_admin_user(request.user):
        messages.error(request, "Permission denied: Only administrators can create new features.")
        return redirect('core:features')

    if request.method == 'POST':
        form = PlatformFeatureForm(request.POST)
        if form.is_valid():
            feature = form.save(commit=False)
            feature.created_by = request.user
            feature.save()
            messages.success(request, f'🎉 Feature "{feature.title}" has been created successfully and is now active for users!')
            return redirect('core:features')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PlatformFeatureForm()

    context = {
        'form': form,
        'title': 'Add New Platform Feature',
        'subtitle': 'Define a new capability, tool, or learning section that users can access directly across the platform.',
        'action_name': 'Create & Publish Feature',
    }
    return render(request, 'core/feature_form.html', context)


@login_required
def edit_feature(request, pk):
    """Admin controller to edit an existing platform feature."""
    if not is_admin_user(request.user):
        messages.error(request, "Permission denied: Only administrators can edit features.")
        return redirect('core:features')

    feature = get_object_or_404(PlatformFeature, pk=pk)

    if request.method == 'POST':
        form = PlatformFeatureForm(request.POST, instance=feature)
        if form.is_valid():
            feature = form.save()
            messages.success(request, f'✅ Feature "{feature.title}" has been updated successfully!')
            return redirect('core:features')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PlatformFeatureForm(instance=feature)

    context = {
        'form': form,
        'feature': feature,
        'title': f'Edit Feature: {feature.title}',
        'subtitle': 'Update titles, target access links, highlights, or visibility status.',
        'action_name': 'Save Changes',
    }
    return render(request, 'core/feature_form.html', context)


@login_required
def delete_feature(request, pk):
    """Admin controller to remove a platform feature."""
    if not is_admin_user(request.user):
        messages.error(request, "Permission denied: Only administrators can delete features.")
        return redirect('core:features')

    feature = get_object_or_404(PlatformFeature, pk=pk)

    if request.method == 'POST':
        title = feature.title
        feature.delete()
        messages.success(request, f'🗑️ Feature "{title}" has been deleted.')
        return redirect('core:features')

    context = {
        'feature': feature,
    }
    return render(request, 'core/feature_confirm_delete.html', context)



def about(request):
    return render(request, 'core/about.html')


def contact(request):
    submitted = False
    if request.method == 'POST':
        submitted = True
    return render(request, 'core/contact.html', {'submitted': submitted})


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'core/terms_of_service.html')

