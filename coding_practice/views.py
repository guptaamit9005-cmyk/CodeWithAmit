import json
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import (
    PracticeSet,
    ProblemCategory,
    CodingQuestion,
    UserQuestionStatus,
    SubmissionRecord,
    ProblemDiscussion,
    DiscussionComment,
    CodingContest,
    ContestParticipant,
    SavedCodeSnippet
)
from .forms import CodingQuestionForm, PracticeSetForm
from .piston_engine import execute_code
from accounts.models import check_and_award_badges

def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def problem_list(request):
    """
    Practice Sets Hub & Problems Portal:
    Displays course-like Practice Sets (Tracks) cards, POTD banner, filter by status/difficulty, and statistics.
    """
    practice_sets = PracticeSet.objects.all().prefetch_related('questions')
    for pset in practice_sets:
        pset.user_progress = pset.get_user_progress(request.user)

    questions = CodingQuestion.objects.all().select_related('category', 'practice_set')
    categories = ProblemCategory.objects.all()

    category_slug = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    platform = request.GET.get('platform')
    status_filter = request.GET.get('status')
    query = request.GET.get('q', '').strip()

    if category_slug:
        questions = questions.filter(category__slug=category_slug)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if platform:
        questions = questions.filter(platform=platform)
    if query:
        questions = questions.filter(title__icontains=query)

    # User solve status mapping
    user_status_map = {}
    bookmarked_ids = set()
    solved_count = 0

    if request.user.is_authenticated:
        statuses = UserQuestionStatus.objects.filter(user=request.user)
        for s in statuses:
            user_status_map[s.question_id] = s.status
            if s.status == 'solved':
                solved_count += 1
            if s.is_bookmarked:
                bookmarked_ids.add(s.question_id)

        if status_filter:
            if status_filter == 'solved':
                solved_ids = [qid for qid, st in user_status_map.items() if st == 'solved']
                questions = questions.filter(id__in=solved_ids)
            elif status_filter == 'attempted':
                att_ids = [qid for qid, st in user_status_map.items() if st == 'attempted']
                questions = questions.filter(id__in=att_ids)
            elif status_filter == 'unattempted':
                done_ids = list(user_status_map.keys())
                questions = questions.exclude(id__in=done_ids)

    # Attach computed status to question objects
    all_questions_list = list(questions)
    for q in all_questions_list:
        q.current_user_status = user_status_map.get(q.id, 'unattempted')
        q.is_bookmarked_by_user = (q.id in bookmarked_ids)

    # Overall stats
    total_db_questions = CodingQuestion.objects.count()
    easy_count = CodingQuestion.objects.filter(difficulty='Easy').count()
    med_count = CodingQuestion.objects.filter(difficulty='Medium').count()
    hard_count = CodingQuestion.objects.filter(difficulty='Hard').count()

    # Problem of the Day (POTD)
    potd = CodingQuestion.objects.filter(is_daily_challenge=True).first()
    if not potd:
        potd = CodingQuestion.objects.first()
    potd_solved = False
    if potd and request.user.is_authenticated:
        potd_solved = (user_status_map.get(potd.id) == 'solved')

    # Upcoming / Live Contest banner
    active_contest = CodingContest.objects.filter(is_active=True).first()

    context = {
        'questions': all_questions_list,
        'practice_sets': practice_sets,
        'categories': categories,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'selected_platform': platform,
        'selected_status': status_filter,
        'query': query,
        'difficulty_choices': CodingQuestion.DIFFICULTY_CHOICES,
        'platform_choices': CodingQuestion.PLATFORM_CHOICES,
        'potd': potd,
        'potd_solved': potd_solved,
        'active_contest': active_contest,
        'stats': {
            'total': total_db_questions,
            'solved': solved_count,
            'easy': easy_count,
            'medium': med_count,
            'hard': hard_count,
            'progress_percent': int((solved_count / total_db_questions * 100)) if total_db_questions > 0 else 0
        },
        'is_admin': is_admin_or_staff(request.user),
    }
    return render(request, 'coding_practice/problem_list.html', context)


def problem_detail(request, slug):
    question = get_object_or_404(CodingQuestion, slug=slug)
    user_status = None
    saved_code = question.starter_code_python or f"# Solution for {question.title}\n\ndef solution():\n    pass\n"
    selected_language = 'python'

    if request.user.is_authenticated:
        user_status = UserQuestionStatus.objects.filter(user=request.user, question=question).first()
        if user_status and user_status.user_code:
            saved_code = user_status.user_code
            selected_language = user_status.selected_language

    recent_submissions = []
    if request.user.is_authenticated:
        recent_submissions = SubmissionRecord.objects.filter(
            user=request.user,
            question=question
        ).order_by('-submitted_at')[:5]

    # Discussions for this problem
    discussions = question.discussions.all().select_related('author', 'author__profile').prefetch_related('comments', 'upvotes')

    context = {
        'question': question,
        'user_status': user_status,
        'saved_code': saved_code,
        'selected_language': selected_language,
        'recent_submissions': recent_submissions,
        'discussions': discussions,
        'hints_list': question.get_hints_list(),
        'company_tags': question.get_company_tags_list(),
        'solve_url': question.get_solve_url(),
        'is_admin': is_admin_or_staff(request.user),
    }
    return render(request, 'coding_practice/problem_detail.html', context)


@login_required
def run_code(request, slug):
    """Execution on website disabled; problem solving is done directly on LeetCode."""
    return JsonResponse({
        'success': False,
        'status': 'Disabled',
        'message': 'Direct code execution on the website is disabled. Please solve this problem on LeetCode.'
    })


@login_required
def submit_code(request, slug):
    """Submission on website disabled; problem solving is done directly on LeetCode."""
    return JsonResponse({
        'success': False,
        'status': 'Disabled',
        'message': 'Direct code submission on the website is disabled. Please solve and submit this problem on LeetCode, then mark it as solved.'
    })






@login_required
def toggle_solved(request, slug):
    """1-click toggle to mark a question as Solved or Unattempted by the student."""
    question = get_object_or_404(CodingQuestion, slug=slug)
    user_status, created = UserQuestionStatus.objects.get_or_create(user=request.user, question=question)

    if user_status.status == 'solved':
        user_status.status = 'unattempted'
        user_status.solved_at = None
        new_status = 'unattempted'
        msg = f"Marked '{question.title}' as unattempted."
    else:
        user_status.status = 'solved'
        user_status.solved_at = timezone.now()
        new_status = 'solved'
        
        points_to_award = question.points
        if question.is_daily_challenge:
            points_to_award += 50

        msg = f"🎉 Great job! Marked '{question.title}' as Solved (+{points_to_award} XP)!"
        
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile.points += points_to_award
            profile.update_streak()
            profile.save()

        check_and_award_badges(request.user)

    user_status.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({'success': True, 'status': new_status, 'message': msg})

    messages.success(request, msg)
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('coding_practice:problem_list')


@login_required
def toggle_bookmark(request, slug):
    question = get_object_or_404(CodingQuestion, slug=slug)
    user_status, _ = UserQuestionStatus.objects.get_or_create(user=request.user, question=question)
    user_status.is_bookmarked = not user_status.is_bookmarked
    user_status.save()

    status_str = "added to" if user_status.is_bookmarked else "removed from"
    messages.info(request, f"Problem '{question.title}' {status_str} your bookmarks.")
    return redirect('coding_practice:problem_detail', slug=slug)


# ==========================================
# PROBLEM DISCUSSIONS & SOLUTIONS FORUM
# ==========================================

@login_required
def create_discussion(request, slug):
    question = get_object_or_404(CodingQuestion, slug=slug)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'solution')
        language = request.POST.get('language', 'python')
        content = request.POST.get('content', '').strip()
        code_snippet = request.POST.get('code_snippet', '').strip()
        youtube_url = request.POST.get('youtube_url', '').strip()

        if title and content:
            discussion = ProblemDiscussion.objects.create(
                question=question,
                author=request.user,
                title=title,
                category=category,
                language=language,
                content=content,
                code_snippet=code_snippet,
                youtube_url=youtube_url
            )
            # Award points for contributing
            if hasattr(request.user, 'profile'):
                request.user.profile.points += 15
                request.user.profile.save(update_fields=['points'])
            check_and_award_badges(request.user)

            messages.success(request, "🎉 Your solution/discussion has been posted (+15 XP)!")
        else:
            messages.error(request, "Please provide both a title and content for your post.")

    return redirect('coding_practice:problem_detail', slug=slug)


@login_required
def toggle_discussion_upvote(request, discussion_id):
    discussion = get_object_or_404(ProblemDiscussion, id=discussion_id)
    if request.user in discussion.upvotes.all():
        discussion.upvotes.remove(request.user)
        upvoted = False
    else:
        discussion.upvotes.add(request.user)
        upvoted = True
        # Reward author
        if hasattr(discussion.author, 'profile'):
            discussion.author.profile.points += 5
            discussion.author.profile.save(update_fields=['points'])

    return JsonResponse({
        'success': True,
        'upvoted': upvoted,
        'total_upvotes': discussion.total_upvotes
    })


@login_required
def add_discussion_comment(request, discussion_id):
    discussion = get_object_or_404(ProblemDiscussion, id=discussion_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            DiscussionComment.objects.create(
                discussion=discussion,
                author=request.user,
                comment=comment_text
            )
            messages.success(request, "Comment posted successfully!")
    return redirect('coding_practice:problem_detail', slug=discussion.question.slug)


# ==========================================
# WEEKLY / WEEKEND CODING CONTESTS
# ==========================================

def contest_list(request):
    """Weekly & Weekend Coding Contests hub with live countdowns and registration."""
    contests = CodingContest.objects.filter(is_active=True).prefetch_related('participants')
    
    registered_contest_ids = set()
    if request.user.is_authenticated:
        registered_contest_ids = set(
            ContestParticipant.objects.filter(user=request.user).values_list('contest_id', flat=True)
        )

    # Seed sample contest if none exist
    if not contests.exists():
        now = timezone.now()
        q_subset = CodingQuestion.objects.all()[:3]
        demo_contest = CodingContest.objects.create(
            title="Codestyle Weekly Sprint #42",
            description="Compete with top coders across colleges in a 90-minute timed DSA sprint. Solve 3 algorithm challenges and climb the live podium!",
            badge_label="Weekly Contest",
            start_time=now + timezone.timedelta(hours=2),
            end_time=now + timezone.timedelta(hours=3, minutes=30),
            duration_minutes=90,
            prize_xp=500
        )
        demo_contest.questions.set(q_subset)
        contests = CodingContest.objects.filter(is_active=True)

    return render(request, 'coding_practice/contest_list.html', {
        'contests': contests,
        'registered_contest_ids': registered_contest_ids,
    })


def contest_detail(request, slug):
    contest = get_object_or_404(CodingContest, slug=slug)
    is_registered = False
    participant_record = None

    if request.user.is_authenticated:
        participant_record = ContestParticipant.objects.filter(contest=contest, user=request.user).first()
        is_registered = bool(participant_record)

    questions = contest.questions.all()
    participants = contest.participants.select_related('user', 'user__profile').order_by('-score', 'time_taken_seconds')[:20]

    return render(request, 'coding_practice/contest_detail.html', {
        'contest': contest,
        'is_registered': is_registered,
        'participant_record': participant_record,
        'questions': questions,
        'participants': participants,
    })


@login_required
def register_contest(request, slug):
    contest = get_object_or_404(CodingContest, slug=slug)
    participant, created = ContestParticipant.objects.get_or_create(contest=contest, user=request.user)
    
    if created:
        messages.success(request, f"🎉 You have successfully registered for {contest.title}! Good luck!")
        check_and_award_badges(request.user)
    else:
        messages.info(request, f"You are already registered for {contest.title}.")

    return redirect('coding_practice:contest_detail', slug=slug)


def contest_leaderboard(request, slug):
    contest = get_object_or_404(CodingContest, slug=slug)
    participants = contest.participants.select_related('user', 'user__profile').order_by('-score', 'time_taken_seconds')
    return render(request, 'coding_practice/contest_leaderboard.html', {
        'contest': contest,
        'participants': participants,
    })


# ==========================================
# PRACTICE SETS (COURSE-LIKE TRACKS) VIEWS
# ==========================================

def practice_set_detail(request, slug):
    """
    Dedicated view for a single Practice Set (Course-like track view).
    Lists questions in this set with category filters, difficulty filters, search, and YouTube solution links.
    """
    practice_set = get_object_or_404(PracticeSet, slug=slug)
    questions = CodingQuestion.objects.filter(practice_set=practice_set).select_related('category', 'practice_set')

    query = request.GET.get('q', '').strip()
    difficulty = request.GET.get('difficulty')
    category_slug = request.GET.get('category')
    status_filter = request.GET.get('status')

    if query:
        questions = questions.filter(title__icontains=query)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if category_slug:
        questions = questions.filter(category__slug=category_slug)

    # User solve status mapping
    user_status_map = {}
    bookmarked_ids = set()
    solved_in_set = 0

    if request.user.is_authenticated:
        statuses = UserQuestionStatus.objects.filter(
            user=request.user,
            question__practice_set=practice_set
        )
        for s in statuses:
            user_status_map[s.question_id] = s.status
            if s.status == 'solved':
                solved_in_set += 1
            if s.is_bookmarked:
                bookmarked_ids.add(s.question_id)

        if status_filter:
            if status_filter == 'solved':
                solved_ids = [qid for qid, st in user_status_map.items() if st == 'solved']
                questions = questions.filter(id__in=solved_ids)
            elif status_filter == 'attempted':
                att_ids = [qid for qid, st in user_status_map.items() if st == 'attempted']
                questions = questions.filter(id__in=att_ids)
            elif status_filter == 'unattempted':
                done_ids = list(user_status_map.keys())
                questions = questions.exclude(id__in=done_ids)

    all_questions_list = list(questions)
    for q in all_questions_list:
        q.current_user_status = user_status_map.get(q.id, 'unattempted')
        q.is_bookmarked_by_user = (q.id in bookmarked_ids)

    # Topics present in this set
    categories = ProblemCategory.objects.filter(questions__practice_set=practice_set).distinct()

    total_in_set = practice_set.questions.count()
    easy_count = practice_set.questions.filter(difficulty='Easy').count()
    med_count = practice_set.questions.filter(difficulty='Medium').count()
    hard_count = practice_set.questions.filter(difficulty='Hard').count()
    progress_percent = int((solved_in_set / total_in_set * 100)) if total_in_set > 0 else 0

    context = {
        'practice_set': practice_set,
        'questions': all_questions_list,
        'categories': categories,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'selected_status': status_filter,
        'query': query,
        'difficulty_choices': CodingQuestion.DIFFICULTY_CHOICES,
        'stats': {
            'total': total_in_set,
            'solved': solved_in_set,
            'easy': easy_count,
            'medium': med_count,
            'hard': hard_count,
            'progress_percent': progress_percent
        },
        'is_admin': is_admin_or_staff(request.user),
    }
    return render(request, 'coding_practice/practice_set_detail.html', context)


@login_required
@user_passes_test(is_admin_or_staff)
def add_practice_set(request):
    if request.method == 'POST':
        form = PracticeSetForm(request.POST)
        if form.is_valid():
            pset = form.save()
            messages.success(request, f"Practice Set '{pset.title}' created successfully!")
            return redirect('coding_practice:practice_set_detail', slug=pset.slug)
    else:
        form = PracticeSetForm()

    return render(request, 'coding_practice/practice_set_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
@user_passes_test(is_admin_or_staff)
def edit_practice_set(request, slug):
    pset = get_object_or_404(PracticeSet, slug=slug)
    if request.method == 'POST':
        form = PracticeSetForm(request.POST, instance=pset)
        if form.is_valid():
            pset = form.save()
            messages.success(request, f"Practice Set '{pset.title}' updated successfully!")
            return redirect('coding_practice:practice_set_detail', slug=pset.slug)
    else:
        form = PracticeSetForm(instance=pset)

    return render(request, 'coding_practice/practice_set_form.html', {
        'form': form,
        'is_edit': True,
        'practice_set': pset,
    })


@login_required
@user_passes_test(is_admin_or_staff)
def delete_practice_set(request, slug):
    pset = get_object_or_404(PracticeSet, slug=slug)
    if request.method == 'POST':
        title = pset.title
        pset.delete()
        messages.success(request, f"Practice Set '{title}' has been deleted.")
        return redirect('coding_practice:problem_list')
    return render(request, 'coding_practice/practice_set_confirm_delete.html', {'practice_set': pset})


# Admin Question Management
@login_required
@user_passes_test(is_admin_or_staff)
def add_question(request):
    set_slug = request.GET.get('set')
    preselected_set = PracticeSet.objects.filter(slug=set_slug).first() if set_slug else None

    if request.method == 'POST':
        form = CodingQuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            messages.success(request, f"Problem '{question.title}' added successfully!")
            if question.practice_set:
                return redirect('coding_practice:practice_set_detail', slug=question.practice_set.slug)
            return redirect('coding_practice:problem_list')
    else:
        initial = {'platform': 'LeetCode', 'points': 10}
        if preselected_set:
            initial['practice_set'] = preselected_set
        form = CodingQuestionForm(initial=initial)

    categories = ProblemCategory.objects.all()
    practice_sets = PracticeSet.objects.all()
    return render(request, 'coding_practice/question_form.html', {
        'form': form,
        'is_edit': False,
        'categories': categories,
        'practice_sets': practice_sets,
        'preselected_set': preselected_set,
    })


@login_required
@user_passes_test(is_admin_or_staff)
def edit_question(request, slug):
    question = get_object_or_404(CodingQuestion, slug=slug)
    if request.method == 'POST':
        form = CodingQuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            messages.success(request, f"Problem '{question.title}' updated successfully!")
            if question.practice_set:
                return redirect('coding_practice:practice_set_detail', slug=question.practice_set.slug)
            return redirect('coding_practice:problem_list')
    else:
        form = CodingQuestionForm(instance=question)

    practice_sets = PracticeSet.objects.all()
    categories = ProblemCategory.objects.all()
    return render(request, 'coding_practice/question_form.html', {
        'form': form,
        'is_edit': True,
        'question': question,
        'practice_sets': practice_sets,
        'categories': categories,
    })


@login_required
@user_passes_test(is_admin_or_staff)
def delete_question(request, slug):
    question = get_object_or_404(CodingQuestion, slug=slug)
    practice_set_slug = question.practice_set.slug if question.practice_set else None
    if request.method == 'POST':
        title = question.title
        question.delete()
        messages.success(request, f"Problem '{title}' has been deleted.")
        if practice_set_slug:
            return redirect('coding_practice:practice_set_detail', slug=practice_set_slug)
        return redirect('coding_practice:problem_list')
    return render(request, 'coding_practice/question_confirm_delete.html', {'question': question})


# ==============================================================================
# MULTI-LANGUAGE CODE COMPILER & WEB SANDBOX VIEWS
# Supports: Python, C, C++, HTML, JavaScript, CSS
# ==============================================================================

def code_editor(request):
    """
    Main Code Editor & Compiler interface.
    Supports Python, C, C++, HTML/CSS/JS with live execution & preview,
    file downloading, and persistent saving.
    """
    initial_lang = request.GET.get('lang', 'python').lower()
    snippet_id = request.GET.get('snippet_id')
    loaded_snippet = None

    if snippet_id:
        try:
            if request.user.is_authenticated:
                loaded_snippet = SavedCodeSnippet.objects.filter(id=snippet_id, user=request.user).first()
            else:
                loaded_snippet = SavedCodeSnippet.objects.filter(id=snippet_id).first()
            if loaded_snippet:
                initial_lang = loaded_snippet.language
        except Exception:
            pass

    user_snippets = []
    if request.user.is_authenticated:
        user_snippets = SavedCodeSnippet.objects.filter(user=request.user).order_by('-updated_at')

    context = {
        'initial_lang': initial_lang,
        'loaded_snippet': loaded_snippet,
        'user_snippets': user_snippets,
    }
    return render(request, 'coding_practice/code_editor.html', context)


@csrf_exempt
def run_sandbox_code(request):
    """
    API endpoint to execute code (Python, C, C++, JavaScript).
    Returns real or sandboxed stdout/stderr, execution time, and exit status.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    code = data.get('code', '')
    language = data.get('language', 'python')
    stdin = data.get('stdin', '')

    if not code.strip():
        return JsonResponse({
            'success': False,
            'output': 'Error: No code provided to execute.',
            'stdout': '',
            'stderr': 'Empty input source',
            'exit_code': 1,
            'runtime_ms': 0
        })

    result = execute_code(language=language, code=code, stdin=stdin)
    return JsonResponse(result)


@csrf_exempt
def save_code_snippet(request):
    """
    API endpoint to save code file / snippet.
    Saves title, language, code, and web files (HTML/CSS/JS).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    title = data.get('title', '').strip() or 'Untitled Snippet'
    language = data.get('language', 'python')
    code = data.get('code', '')
    html_code = data.get('html_code', '')
    css_code = data.get('css_code', '')
    js_code = data.get('js_code', '')
    stdin_input = data.get('stdin_input', '')
    snippet_id = data.get('snippet_id')

    user = request.user if request.user.is_authenticated else None

    if snippet_id:
        snippet = SavedCodeSnippet.objects.filter(id=snippet_id).first()
        if snippet:
            # If user owns it or it's public
            if user and snippet.user and snippet.user != user:
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            snippet.title = title
            snippet.language = language
            snippet.code = code
            snippet.html_code = html_code
            snippet.css_code = css_code
            snippet.js_code = js_code
            snippet.stdin_input = stdin_input
            if user and not snippet.user:
                snippet.user = user
            snippet.save()
            return JsonResponse({
                'success': True,
                'snippet_id': snippet.id,
                'title': snippet.title,
                'message': 'File updated successfully!'
            })

    # Create new snippet
    snippet = SavedCodeSnippet.objects.create(
        user=user,
        title=title,
        language=language,
        code=code,
        html_code=html_code,
        css_code=css_code,
        js_code=js_code,
        stdin_input=stdin_input
    )

    return JsonResponse({
        'success': True,
        'snippet_id': snippet.id,
        'title': snippet.title,
        'message': 'File saved successfully!'
    })


def load_code_snippet_api(request, snippet_id):
    """
    API endpoint to fetch a saved snippet's details via AJAX.
    """
    snippet = get_object_or_404(SavedCodeSnippet, id=snippet_id)
    return JsonResponse({
        'success': True,
        'id': snippet.id,
        'title': snippet.title,
        'language': snippet.language,
        'code': snippet.code,
        'html_code': snippet.html_code,
        'css_code': snippet.css_code,
        'js_code': snippet.js_code,
        'stdin_input': snippet.stdin_input,
        'updated_at': snippet.updated_at.strftime("%b %d, %Y %H:%M")
    })


@csrf_exempt
def delete_code_snippet(request, snippet_id):
    """
    API endpoint to delete a saved snippet.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    snippet = get_object_or_404(SavedCodeSnippet, id=snippet_id)
    if request.user.is_authenticated and snippet.user and snippet.user != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    snippet.delete()
    return JsonResponse({'success': True, 'message': 'Snippet deleted successfully!'})

