from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import StudentRegistrationForm, UserProfileUpdateForm
from .models import UserProfile
from courses.models import Enrollment
from coding_practice.models import UserQuestionStatus
from notes.models import Note

def register_view(request):
    initial_role = request.GET.get('role', 'student')
    if initial_role not in ['student', 'admin', 'instructor']:
        initial_role = 'student'

    if request.method == 'POST':
        # If user is already logged in, log out so the new account can be created and logged into
        if request.user.is_authenticated:
            logout(request)

        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            
            role = form.cleaned_data.get('role', 'student')
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            elif role == 'instructor':
                user.is_staff = True
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

            messages.success(request, f"🎉 Welcome to CodeByAmit, {user.username}! Your {profile.get_role_display()} account has been created.")
            login(request, user)
            
            if role == 'admin':
                return redirect('dashboard:admin_dashboard')
            elif role == 'instructor':
                return redirect('dashboard:instructor_dashboard')
            return redirect('dashboard:student_dashboard')
        else:
            messages.error(request, "Please check the highlighted errors below.")
    else:
        form = StudentRegistrationForm(initial={'role': initial_role})

    return render(request, 'accounts/register.html', {
        'form': form,
        'initial_role': initial_role
    })


def login_view(request):
    active_role = request.GET.get('role')
    if not active_role:
        next_param = request.GET.get('next', '').lower()
        if 'admin' in next_param:
            active_role = 'admin'
        else:
            active_role = 'student'

    if active_role not in ['student', 'admin']:
        active_role = 'student'

    # If already logged in:
    if request.user.is_authenticated and not request.GET.get('switch'):
        is_currently_admin = request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
        # Only auto-redirect if they're not trying to switch to a different role portal
        if is_currently_admin and active_role == 'admin' and request.method == 'GET':
            return redirect('dashboard:admin_dashboard')
        elif not is_currently_admin and active_role == 'student' and request.method == 'GET':
            return redirect('dashboard:student_dashboard')

    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)

        form = AuthenticationForm(request, data=request.POST)
        role_tab = request.POST.get('portal_role', active_role)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Update user streak
            if hasattr(user, 'profile'):
                user.profile.update_streak()

            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            is_admin_user = user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin')
            if role_tab == 'admin' or is_admin_user:
                return redirect('dashboard:admin_dashboard')
            elif hasattr(user, 'profile') and user.profile.role == 'instructor':
                return redirect('dashboard:instructor_dashboard')
            else:
                return redirect('dashboard:student_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'active_role': active_role
    })


def admin_login_view(request):
    """Direct route for Admin Login Portal."""
    get_params = request.GET.copy()
    get_params['role'] = 'admin'
    request.GET = get_params
    return login_view(request)


def student_login_view(request):
    """Direct route for Student Login Portal."""
    get_params = request.GET.copy()
    get_params['role'] = 'student'
    request.GET = get_params
    return login_view(request)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')


@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Check and award badges if own profile
    if user == request.user:
        from .models import check_and_award_badges
        check_and_award_badges(user)

    enrollments = Enrollment.objects.filter(user=user).select_related('course')
    solved_questions = UserQuestionStatus.objects.filter(user=user, status='solved').select_related('question')
    uploaded_notes = Note.objects.filter(uploader=user)
    user_badges = user.badges.select_related('badge')

    context = {
        'profile_user': user,
        'profile': profile,
        'enrollments': enrollments,
        'solved_questions': solved_questions,
        'uploaded_notes': uploaded_notes,
        'user_badges': user_badges,
        'is_own_profile': (user == request.user),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update User fields
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()

            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = UserProfileUpdateForm(instance=profile, initial=initial_data)

    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': profile})


def leaderboard_view(request):
    """Global XP & Streak Leaderboard with Badges Showcase and Podium."""
    from .models import Badge, check_and_award_badges

    if request.user.is_authenticated:
        check_and_award_badges(request.user)

    # Top students by points & streaks
    profiles = list(UserProfile.objects.select_related('user').prefetch_related('user__badges__badge').order_by('-points', '-streak_count')[:50])

    # Attach solved counts to list items
    from coding_practice.models import UserQuestionStatus
    for idx, p in enumerate(profiles, start=1):
        p.rank = idx
        p.solved_count = UserQuestionStatus.objects.filter(user=p.user, status='solved').count()

    top_3 = profiles[:3]
    rest = profiles[3:]

    all_badges = Badge.objects.all()

    user_rank = None
    if request.user.is_authenticated:
        for p in profiles:
            if p.user == request.user:
                user_rank = p.rank
                break

    return render(request, 'accounts/leaderboard.html', {
        'profiles': profiles,
        'top_3': top_3,
        'rest': rest,
        'all_badges': all_badges,
        'user_rank': user_rank,
    })

