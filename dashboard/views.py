from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from courses.models import Course, Enrollment, LessonProgress, Lesson
from live_classes.models import LiveClass, ClassAttendee
from coding_practice.models import CodingQuestion, UserQuestionStatus, SubmissionRecord
from roadmaps.models import Roadmap, UserRoadmapEnrollment
from tutorials.models import TutorialTopic, TutorialCategory
from notes.models import Note
from accounts.models import UserProfile, Badge, UserBadge, check_and_award_badges
from code_sources.models import CodeSource
from community.models import DoubtQuestion
from courses.forms import CourseForm, LessonForm
from live_classes.forms import LiveClassScheduleForm
from roadmaps.forms import RoadmapForm
from coding_practice.forms import CodingQuestionForm
from tutorials.forms import TutorialTopicForm
from core.models import PlatformFeature


@login_required
def student_dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # 0. Automatically update user streak on dashboard visit
    profile.update_streak()

    # 1. Enrolled courses & progress
    enrollments = Enrollment.objects.filter(user=user).select_related('course', 'course__category').order_by('-enrolled_at')
    enrolled_courses_data = []
    completed_courses_count = 0
    in_progress_courses_count = 0
    primary_course = None

    for enr in enrollments:
        progress_pct = enr.course.get_progress_for_user(user)
        # Find next uncompleted lesson
        completed_lessons = LessonProgress.objects.filter(
            user=user,
            lesson__course=enr.course,
            is_completed=True
        ).values_list('lesson_id', flat=True)
        next_lesson = enr.course.lessons.exclude(id__in=completed_lessons).order_by('order').first()
        if not next_lesson:
            next_lesson = enr.course.lessons.first()

        course_item = {
            'enrollment': enr,
            'course': enr.course,
            'progress_pct': progress_pct,
            'next_lesson': next_lesson,
            'completed_lessons_count': len(completed_lessons),
            'total_lessons': enr.course.lessons.count(),
        }
        enrolled_courses_data.append(course_item)

        if progress_pct >= 100:
            completed_courses_count += 1
        else:
            in_progress_courses_count += 1
            if not primary_course and next_lesson:
                primary_course = course_item

    # Fallback primary course
    if not primary_course and enrolled_courses_data:
        primary_course = enrolled_courses_data[0]

    total_completed_lessons = LessonProgress.objects.filter(user=user, is_completed=True).count()

    # 2. Upcoming live classes
    now = timezone.now()
    registered_class_ids = ClassAttendee.objects.filter(user=user).values_list('live_class_id', flat=True)
    upcoming_classes_qs = LiveClass.objects.filter(
        id__in=registered_class_ids,
        status__in=['upcoming', 'live']
    ).order_by('scheduled_date', 'start_time')
    live_now_class = upcoming_classes_qs.filter(status='live').first()
    upcoming_classes = upcoming_classes_qs[:5]

    # 3. Coding Practice Statistics & LeetCode-style Breakdown
    solved_count = UserQuestionStatus.objects.filter(user=user, status='solved').count()
    attempted_count = UserQuestionStatus.objects.filter(user=user, status='attempted').count()
    total_questions = CodingQuestion.objects.count()

    easy_total = CodingQuestion.objects.filter(difficulty='Easy').count()
    easy_solved = UserQuestionStatus.objects.filter(user=user, status='solved', question__difficulty='Easy').count()
    easy_pct = int((easy_solved / easy_total * 100)) if easy_total > 0 else 0

    medium_total = CodingQuestion.objects.filter(difficulty='Medium').count()
    medium_solved = UserQuestionStatus.objects.filter(user=user, status='solved', question__difficulty='Medium').count()
    medium_pct = int((medium_solved / medium_total * 100)) if medium_total > 0 else 0

    hard_total = CodingQuestion.objects.filter(difficulty='Hard').count()
    hard_solved = UserQuestionStatus.objects.filter(user=user, status='solved', question__difficulty='Hard').count()
    hard_pct = int((hard_solved / hard_total * 100)) if hard_total > 0 else 0

    overall_solved_pct = int((solved_count / total_questions * 100)) if total_questions > 0 else 0

    recent_submissions = SubmissionRecord.objects.filter(user=user).select_related('question').order_by('-submitted_at')[:5]

    # Daily challenge
    daily_challenge = CodingQuestion.objects.filter(is_daily_challenge=True).first()
    if not daily_challenge:
        daily_challenge = CodingQuestion.objects.first()
    daily_solved = False
    if daily_challenge:
        daily_solved = UserQuestionStatus.objects.filter(user=user, question=daily_challenge, status='solved').exists()

    # Bookmarked coding questions
    bookmarked_questions = CodingQuestion.objects.filter(
        user_statuses__user=user,
        user_statuses__is_bookmarked=True
    ).select_related('category')[:4]

    # 4. Active Roadmaps
    roadmap_enrollments = UserRoadmapEnrollment.objects.filter(user=user).select_related('roadmap')
    roadmaps_data = []
    for renr in roadmap_enrollments:
        pct = renr.roadmap.get_user_completion_percent(user)
        roadmaps_data.append({
            'roadmap': renr.roadmap,
            'progress_pct': pct,
            'total_topics': renr.roadmap.total_topics,
        })

    # 6. Gamification / Student Level & Progress
    # Check & award any newly unlocked badges automatically
    check_and_award_badges(user)
    profile.refresh_from_db()

    level = (profile.points // 100) + 1
    xp_in_level = profile.points % 100
    xp_needed_for_next = 100 - xp_in_level
    level_progress_pct = min(100, xp_in_level)

    level_titles = {
        1: "Novice Coder",
        2: "Syntax Explorer",
        3: "Algorithm Apprentice",
        4: "Logic Luminary",
        5: "Byte Master",
        6: "Code Alchemist",
        7: "Fullstack Architect",
        8: "DSA Grandmaster",
    }
    level_title = level_titles.get(level, "Legendary Engineer")

    # User Badges & Locked Badges
    earned_user_badges = list(user.badges.select_related('badge').order_by('-awarded_at'))
    earned_badge_ids = {ub.badge_id for ub in earned_user_badges}
    all_platform_badges = list(Badge.objects.all())
    locked_badges = [b for b in all_platform_badges if b.id not in earned_badge_ids]
    total_badges_count = len(all_platform_badges)
    earned_badges_count = len(earned_user_badges)
    badge_completion_pct = int((earned_badges_count / total_badges_count) * 100) if total_badges_count > 0 else 0

    # 7-Day Weekly Streak Timeline (ending today)
    today = timezone.now().date()
    streak_days = []
    for i in range(6, -1, -1):
        d = today - timezone.timedelta(days=i)
        is_active = (i < profile.streak_count)
        streak_days.append({
            'date': d,
            'day_name': d.strftime('%a'),
            'day_num': d.day,
            'is_today': (d == today),
            'is_active': is_active
        })

    # Leaderboard Standing
    higher_points_count = UserProfile.objects.filter(points__gt=profile.points).count()
    user_rank = higher_points_count + 1
    total_students = UserProfile.objects.count()
    top_coders = list(UserProfile.objects.select_related('user').order_by('-points', '-streak_count')[:5])

    # Gamified Daily Quests
    daily_quests = [
        {
            'title': 'Daily Check-in',
            'desc': 'Keep your coding streak on fire today',
            'icon': 'bi-fire',
            'color': 'warning',
            'xp': 10,
            'progress': 1,
            'target': 1,
            'is_completed': True,
        },
        {
            'title': 'Problem of the Day',
            'desc': 'Solve today’s POTD algorithmic challenge',
            'icon': 'bi-lightning-charge-fill',
            'color': 'danger',
            'xp': 25,
            'progress': 1 if daily_solved else 0,
            'target': 1,
            'is_completed': daily_solved,
        },
        {
            'title': 'Practice Set Challenge',
            'desc': 'Solve a curated problem from the practice sets',
            'icon': 'bi-code-square',
            'color': 'primary',
            'xp': 15,
            'progress': 1 if solved_count > 0 else 0,
            'target': 1,
            'is_completed': solved_count > 0,
        },
        {
            'title': 'Batch Lesson Progress',
            'desc': 'Complete course lessons to level up your engineering skills',
            'icon': 'bi-mortarboard-fill',
            'color': 'info',
            'progress': total_completed_lessons,
            'target': max(1, total_completed_lessons + (0 if total_completed_lessons > 0 else 1)),
            'xp': 30,
            'is_completed': total_completed_lessons > 0,
        },
        {
            'title': 'Tutorial Study Session',
            'desc': 'Review topic guides and master core engineering fundamentals',
            'icon': 'bi-book-half',
            'color': 'purple',
            'xp': 20,
            'progress': 1 if total_completed_lessons > 0 else 0,
            'target': 1,
            'is_completed': total_completed_lessons > 0,
        }
    ]

    # Legacy badges list compatibility
    badges = []
    if profile.streak_count >= 1:
        badges.append({'name': 'Ignition', 'desc': 'Active Streak', 'icon': 'bi-fire', 'color': 'warning'})
    if profile.streak_count >= 7:
        badges.append({'name': 'Week Warrior', 'desc': '7-Day Streak', 'icon': 'bi-lightning-charge-fill', 'color': 'danger'})
    if solved_count >= 1:
        badges.append({'name': 'First Solve', 'desc': 'First DSA Problem', 'icon': 'bi-code-square', 'color': 'success'})
    if solved_count >= 10:
        badges.append({'name': 'Algo Adept', 'desc': '10+ Solved', 'icon': 'bi-award-fill', 'color': 'primary'})
    if completed_courses_count >= 1:
        badges.append({'name': 'Graduate', 'desc': 'Course Completed', 'icon': 'bi-mortarboard-fill', 'color': 'info'})
    if profile.points >= 200:
        badges.append({'name': 'XP Master', 'desc': '200+ XP', 'icon': 'bi-gem', 'color': 'purple'})

    # 7. Recommended Courses to explore
    enrolled_ids = enrollments.values_list('course_id', flat=True)
    recommended_courses = Course.objects.filter(is_published=True).exclude(id__in=enrolled_ids).select_related('category')[:3]

    # 8. All Platform Resources for All-in-One Student Dashboard Suite
    tutorial_tracks = TutorialCategory.objects.all().prefetch_related('topics')[:6]
    dsa_questions = CodingQuestion.objects.all().select_related('category')[:30]
    recent_code_sources = CodeSource.objects.select_related('author').order_by('-created_at')[:6]
    recent_doubts = DoubtQuestion.objects.select_related('author').order_by('-created_at')[:6]

    context = {
        'profile': profile,
        'enrolled_courses_data': enrolled_courses_data,
        'in_progress_courses_count': in_progress_courses_count,
        'completed_courses_count': completed_courses_count,
        'primary_course': primary_course,
        'total_completed_lessons': total_completed_lessons,
        'solved_count': solved_count,
        'attempted_count': attempted_count,
        'total_questions': total_questions,
        'overall_solved_pct': overall_solved_pct,
        'easy_solved': easy_solved,
        'easy_total': easy_total,
        'easy_pct': easy_pct,
        'medium_solved': medium_solved,
        'medium_total': medium_total,
        'medium_pct': medium_pct,
        'hard_solved': hard_solved,
        'hard_total': hard_total,
        'hard_pct': hard_pct,
        'recent_submissions': recent_submissions,
        'daily_challenge': daily_challenge,
        'daily_solved': daily_solved,
        'bookmarked_questions': bookmarked_questions,
        'roadmaps_data': roadmaps_data,
        'level': level,
        'xp_in_level': xp_in_level,
        'xp_needed_for_next': xp_needed_for_next,
        'level_progress_pct': level_progress_pct,
        'level_title': level_title,
        'streak_days': streak_days,
        'user_rank': user_rank,
        'total_students': total_students,
        'top_coders': top_coders,
        'earned_user_badges': earned_user_badges,
        'locked_badges': locked_badges,
        'total_badges_count': total_badges_count,
        'earned_badges_count': earned_badges_count,
        'badge_completion_pct': badge_completion_pct,
        'daily_quests': daily_quests,
        'badges': badges,
        'recommended_courses': recommended_courses,
        'tutorial_tracks': tutorial_tracks,
        'dsa_questions': dsa_questions,
        'recent_code_sources': recent_code_sources,
        'recent_doubts': recent_doubts,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
def instructor_dashboard(request):
    if not (request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        return redirect('dashboard:student_dashboard')

    user = request.user
    my_courses = Course.objects.filter(instructor=user).prefetch_related('enrollments', 'lessons')
    my_classes = LiveClass.objects.filter(instructor=user).order_by('-scheduled_date')
    total_students = Enrollment.objects.filter(course__instructor=user).values('user').distinct().count()

    context = {
        'my_courses': my_courses,
        'my_classes': my_classes,
        'total_students': total_students,
    }
    return render(request, 'dashboard/instructor_dashboard.html', context)


from django.db.models import Count
from tutorials.forms import TutorialTopicForm, TutorialCategoryForm

@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('dashboard:student_dashboard')

    metrics = {
        'total_users': User.objects.count(),
        'total_tutorials': TutorialTopic.objects.count(),
        'total_tutorial_categories': TutorialCategory.objects.count(),
        'total_courses': Course.objects.count(),
        'total_coding_questions': CodingQuestion.objects.count(),
        'total_code_sources': CodeSource.objects.count(),
        'total_doubts': DoubtQuestion.objects.count(),
        'total_roadmaps': Roadmap.objects.count(),
        'total_notes': Note.objects.count(),
        'total_features': PlatformFeature.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
        'total_submissions': SubmissionRecord.objects.count(),
    }
    recent_users = User.objects.order_by('-date_joined')[:8]
    recent_topics = TutorialTopic.objects.select_related('category').order_by('-id')[:12]
    all_tutorial_categories = TutorialCategory.objects.annotate(topics_count=Count('topics')).order_by('order', 'name')
    recent_courses = Course.objects.select_related('category', 'instructor').order_by('-created_at')[:8]
    recent_questions = CodingQuestion.objects.select_related('category').order_by('-id')[:8]
    recent_code_sources = CodeSource.objects.select_related('author').order_by('-created_at')[:8]
    recent_roadmaps = Roadmap.objects.order_by('-created_at')[:8]
    recent_notes = Note.objects.select_related('category', 'uploader').order_by('-uploaded_at')[:8]
    recent_features = PlatformFeature.objects.all().order_by('order', '-created_at')[:12]

    recent_lessons = Lesson.objects.select_related('course').order_by('-created_at')[:10]
    all_courses_list = Course.objects.all().order_by('title')

    context = {
        'metrics': metrics,
        'recent_users': recent_users,
        'recent_topics': recent_topics,
        'all_tutorial_categories': all_tutorial_categories,
        'recent_courses': recent_courses,
        'recent_lessons': recent_lessons,
        'all_courses_list': all_courses_list,
        'recent_questions': recent_questions,
        'recent_code_sources': recent_code_sources,
        'recent_roadmaps': recent_roadmaps,
        'recent_features': recent_features,
        'course_form': CourseForm(),
        'lesson_form': LessonForm(),
        'question_form': CodingQuestionForm(),
        'roadmap_form': RoadmapForm(),
        'topic_form': TutorialTopicForm(),
        'category_form': TutorialCategoryForm(),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

