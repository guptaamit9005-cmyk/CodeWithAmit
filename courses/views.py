from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import (
    Course, CourseCategory, CourseSection, SectionLink, Lesson, Quiz, QuizQuestion,
    Enrollment, LessonProgress, CourseBookmark, CourseReview, LessonNote
)
from .forms import CourseForm, LessonForm, QuizQuestionForm, CourseCategoryForm, CourseSectionForm, SectionLinkForm


def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('category', 'instructor').prefetch_related('sections', 'lessons')
    categories = CourseCategory.objects.all()

    category_slug = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    search_query = request.GET.get('q')

    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    if search_query:
        courses = courses.filter(title__icontains=search_query)

    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'search_query': search_query,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    sections = course.sections.prefetch_related('lessons', 'links').order_by('order')
    lessons = course.lessons.select_related('section').order_by('order')
    unsectioned_lessons = course.lessons.filter(section__isnull=True).order_by('order')
    reviews = course.reviews.select_related('user').order_by('-created_at')[:10]

    is_enrolled = False
    is_bookmarked = False
    user_progress = 0

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        is_bookmarked = CourseBookmark.objects.filter(user=request.user, course=course).exists()
        user_progress = course.get_progress_for_user(request.user)

    section_form = CourseSectionForm()
    link_form = SectionLinkForm()

    context = {
        'course': course,
        'sections': sections,
        'unsectioned_lessons': unsectioned_lessons,
        'lessons': lessons,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'is_bookmarked': is_bookmarked,
        'user_progress': user_progress,
        'section_form': section_form,
        'link_form': link_form,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    
    if created:
        messages.success(request, f"Successfully enrolled in '{course.title}'! Let's start learning.")
    else:
        messages.info(request, f"You are already enrolled in '{course.title}'.")

    # Redirect to first lesson if available
    first_lesson = course.lessons.first()
    if first_lesson:
        return redirect('courses:lesson_detail', course_slug=course.slug, lesson_slug=first_lesson.slug)
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    lessons = list(course.lessons.select_related('section').order_by('order'))
    sections = course.sections.prefetch_related('lessons', 'links').order_by('order')
    unsectioned_lessons = course.lessons.filter(section__isnull=True).order_by('order')

    # Check enrollment or free preview
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled and not lesson.is_free_preview and not request.user.is_staff:
        messages.warning(request, "Please enroll in this course to access this lesson.")
        return redirect('courses:course_detail', slug=course.slug)

    # Track progress
    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)

    # Next and Previous lessons
    current_index = lessons.index(lesson)
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None

    # Quiz info
    quiz = getattr(lesson, 'quiz', None)

    # Completed lesson ids for sidebar checkmarks
    completed_lesson_ids = set(
        LessonProgress.objects.filter(
            user=request.user,
            lesson__course=course,
            is_completed=True
        ).values_list('lesson_id', flat=True)
    )

    # Student's timestamped notes for this lesson
    student_notes = lesson.student_notes.filter(user=request.user)

    # Section links (if lesson belongs to a section)
    section_links = lesson.section.links.all().order_by('order') if lesson.section else []

    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'sections': sections,
        'unsectioned_lessons': unsectioned_lessons,
        'section_links': section_links,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'progress': progress,
        'quiz': quiz,
        'student_notes': student_notes,
        'completed_lesson_ids': completed_lesson_ids,
        'course_progress': course.get_progress_for_user(request.user),
    }
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def complete_lesson(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    progress.is_completed = True
    progress.completed_at = timezone.now()
    progress.save()

    # Check if all lessons are completed
    total_lessons = course.lessons.count()
    completed_count = LessonProgress.objects.filter(lesson__course=course, user=request.user, is_completed=True).count()
    if total_lessons > 0 and completed_count >= total_lessons:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if enrollment and not enrollment.is_completed:
            enrollment.is_completed = True
            enrollment.completed_at = timezone.now()
            enrollment.save()
            messages.success(request, f"🎉 Congratulations! You have completed the entire '{course.title}' course!")

    messages.success(request, f"Marked '{lesson.title}' as completed.")
    next_lesson = course.lessons.filter(order__gt=lesson.order).order_by('order').first()
    if next_lesson:
        return redirect('courses:lesson_detail', course_slug=course.slug, lesson_slug=next_lesson.slug)
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def submit_quiz(request, course_slug, lesson_slug):
    if request.method != 'POST':
        return redirect('courses:lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)

    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    quiz = get_object_or_404(Quiz, lesson=lesson)

    questions = quiz.questions.all()
    total_questions = questions.count()
    if total_questions == 0:
        return redirect('courses:lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)

    correct_answers = 0
    feedback = []

    for q in questions:
        user_choice = request.POST.get(f'question_{q.id}')
        is_correct = (user_choice == q.correct_option)
        if is_correct:
            correct_answers += 1
        feedback.append({
            'question': q.question_text,
            'user_choice': user_choice,
            'correct_option': q.correct_option,
            'is_correct': is_correct,
            'explanation': q.explanation
        })

    score_percent = int((correct_answers / total_questions) * 100)
    passed = score_percent >= quiz.passing_score

    if passed:
        # Mark lesson completed
        progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        messages.success(request, f"🎉 You passed the quiz with {score_percent}% ({correct_answers}/{total_questions})! Lesson marked as completed.")
    else:
        messages.warning(request, f"You scored {score_percent}% ({correct_answers}/{total_questions}). Minimum passing score is {quiz.passing_score}%. Review and try again!")

    context = {
        'course': course,
        'lesson': lesson,
        'quiz': quiz,
        'feedback': feedback,
        'score_percent': score_percent,
        'passed': passed,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
    }
    return render(request, 'courses/quiz_result.html', context)


@login_required
def toggle_bookmark(request, slug):
    course = get_object_or_404(Course, slug=slug)
    bookmark = CourseBookmark.objects.filter(user=request.user, course=course)
    if bookmark.exists():
        bookmark.delete()
        messages.info(request, "Removed course from bookmarks.")
    else:
        CourseBookmark.objects.create(user=request.user, course=course)
        messages.success(request, "Course saved to bookmarks.")
    return redirect('courses:course_detail', slug=slug)


@login_required
def add_review(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        if comment:
            CourseReview.objects.update_or_create(
                user=request.user,
                course=course,
                defaults={'rating': rating, 'comment': comment}
            )
            messages.success(request, "Thank you for your review!")
    return redirect('courses:course_detail', slug=slug)


@login_required
def create_course(request):
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only admins or instructors can create courses.")
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.is_published = True
            course.save()
            messages.success(request, f"Course '{course.title}' created and published live! It is now visible to everyone.")
            return redirect('courses:course_detail', slug=course.slug)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm(initial={'is_published': True, 'difficulty': 'Beginner', 'estimated_hours': 10})

    return render(request, 'courses/course_form.html', {'form': form})


@login_required
def edit_course(request, slug):
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only admins or instructors can edit courses.")
        return redirect('courses:course_list')

    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated successfully!")
            return redirect('courses:course_detail', slug=course.slug)
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/course_form.html', {'form': form, 'is_edit': True, 'course': course})


@login_required
def delete_course(request, slug):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can delete courses.")
        return redirect('courses:course_list')

    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f"Course '{title}' has been deleted.")
        return redirect('dashboard:admin_dashboard')

    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@login_required
def add_lesson(request):
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only admins or instructors can add lessons.")
        return redirect('courses:course_list')

    course_slug = request.GET.get('course')
    section_id = request.GET.get('section')
    initial_data = {}
    selected_course = None
    if course_slug:
        selected_course = Course.objects.filter(slug=course_slug).first()
        if selected_course:
            initial_data['course'] = selected_course.pk
            initial_data['order'] = selected_course.lessons.count() + 1
            if section_id:
                initial_data['section'] = section_id

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save()
            messages.success(request, f"Lesson '{lesson.title}' added to course '{lesson.course.title}'!")
            return redirect('courses:lesson_detail', course_slug=lesson.course.slug, lesson_slug=lesson.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = LessonForm(initial=initial_data)

    return render(request, 'courses/lesson_form.html', {'form': form, 'is_edit': False, 'selected_course': selected_course})


# ==========================================
# COURSE SECTIONS & SECTION LINKS MANAGEMENT
# ==========================================

@login_required
def add_section(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only admins or instructors can manage sections.")
        return redirect('courses:course_detail', slug=slug)

    if request.method == 'POST':
        form = CourseSectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.course = course
            if not request.POST.get('order'):
                section.order = course.sections.count() + 1
            section.save()
            messages.success(request, f"Section '{section.title}' created successfully!")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
                return JsonResponse({
                    'success': True,
                    'id': section.id,
                    'title': section.title,
                    'order': section.order,
                    'github_url': section.github_url,
                })
        else:
            messages.error(request, "Failed to create section. Please check form values.")

    next_page = request.POST.get('next') or request.GET.get('next')
    if next_page == 'course_detail':
        return redirect('courses:course_detail', slug=course.slug)
    return redirect('courses:manage_sections', slug=course.slug)


@login_required
def edit_section(request, section_id):
    section = get_object_or_404(CourseSection, id=section_id)
    course = section.course
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Permission denied.")
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        form = CourseSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, f"Section '{section.title}' updated!")
            return redirect('courses:manage_sections', slug=course.slug)
    else:
        form = CourseSectionForm(instance=section)

    return render(request, 'courses/section_form.html', {'form': form, 'section': section, 'course': course})


@login_required
def delete_section(request, section_id):
    section = get_object_or_404(CourseSection, id=section_id)
    course = section.course
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Permission denied.")
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        title = section.title
        section.delete()
        messages.success(request, f"Section '{title}' deleted. Its lessons were preserved.")
        return redirect('courses:manage_sections', slug=course.slug)

    return render(request, 'courses/section_confirm_delete.html', {'section': section, 'course': course})


@login_required
def add_section_link(request, section_id):
    section = get_object_or_404(CourseSection, id=section_id)
    course = section.course
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Permission denied.")
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        form = SectionLinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.section = section
            if not request.POST.get('order'):
                link.order = section.links.count() + 1
            link.save()
            messages.success(request, f"Link '{link.title}' added to section '{section.title}'!")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
                return JsonResponse({
                    'success': True,
                    'id': link.id,
                    'title': link.title,
                    'url': link.url,
                    'link_type': link.link_type,
                    'icon': link.icon_class,
                })
        else:
            messages.error(request, "Failed to add link. Please check the URL format.")

    next_page = request.POST.get('next') or request.GET.get('next')
    if next_page == 'course_detail':
        return redirect('courses:course_detail', slug=course.slug)
    return redirect('courses:manage_sections', slug=course.slug)


@login_required
def delete_section_link(request, link_id):
    link = get_object_or_404(SectionLink, id=link_id)
    course = link.section.course
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Permission denied.")
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        title = link.title
        link.delete()
        messages.success(request, f"Link '{title}' removed.")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
            return JsonResponse({'success': True})
        return redirect('courses:manage_sections', slug=course.slug)

    return redirect('courses:manage_sections', slug=course.slug)


@login_required
def manage_sections(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Permission denied.")
        return redirect('courses:course_detail', slug=course.slug)

    sections = course.sections.prefetch_related('lessons', 'links').order_by('order')
    unsectioned_lessons = course.lessons.filter(section__isnull=True).order_by('order')
    section_form = CourseSectionForm()
    link_form = SectionLinkForm()

    if request.method == 'POST' and request.POST.get('action') == 'assign_lesson':
        lesson_id = request.POST.get('lesson_id')
        sec_id = request.POST.get('section_id')
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
        if sec_id:
            target_sec = get_object_or_404(CourseSection, id=sec_id, course=course)
            lesson.section = target_sec
        else:
            lesson.section = None
        lesson.save()
        messages.success(request, f"Lesson '{lesson.title}' assigned successfully!")
        return redirect('courses:manage_sections', slug=course.slug)

    context = {
        'course': course,
        'sections': sections,
        'unsectioned_lessons': unsectioned_lessons,
        'section_form': section_form,
        'link_form': link_form,
    }
    return render(request, 'courses/manage_sections.html', context)


@login_required
def edit_lesson(request, course_slug, lesson_slug):
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only admins or instructors can edit lessons.")
        return redirect('courses:course_list')

    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lesson '{lesson.title}' updated successfully!")
            return redirect('courses:lesson_detail', course_slug=course.slug, lesson_slug=lesson.slug)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'courses/lesson_form.html', {'form': form, 'is_edit': True, 'lesson': lesson, 'selected_course': course})


@login_required
def delete_lesson(request, course_slug, lesson_slug):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can delete lessons.")
        return redirect('courses:course_list')

    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)

    if request.method == 'POST':
        title = lesson.title
        lesson.delete()
        messages.success(request, f"Lesson '{title}' has been deleted from {course.title}.")
        return redirect('courses:course_detail', slug=course.slug)

    return render(request, 'courses/lesson_confirm_delete.html', {'course': course, 'lesson': lesson})


@login_required
def add_quiz_question(request, course_slug, lesson_slug):
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only admins or instructors can add quiz questions.")
        return redirect('courses:course_list')

    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    quiz, _ = Quiz.objects.get_or_create(lesson=lesson, defaults={'title': f"Quiz: {lesson.title}", 'passing_score': 70})

    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.quiz = quiz
            q.save()
            messages.success(request, f"Quiz question added to lesson '{lesson.title}'!")
            if 'add_another' in request.POST:
                return redirect('courses:add_quiz_question', course_slug=course.slug, lesson_slug=lesson.slug)
            return redirect('courses:lesson_detail', course_slug=course.slug, lesson_slug=lesson.slug)
    else:
        form = QuizQuestionForm()

    existing_questions = quiz.questions.all()
    return render(request, 'courses/quiz_question_form.html', {
        'form': form,
        'course': course,
        'lesson': lesson,
        'quiz': quiz,
        'existing_questions': existing_questions
    })


@login_required
def add_category(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can add categories.")
        return redirect('courses:course_list')

    if request.method == 'POST':
        form = CourseCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Course Category '{cat.name}' created!")
            return redirect('dashboard:admin_dashboard')
    else:
        form = CourseCategoryForm()

    return render(request, 'courses/category_form.html', {'form': form})


# ==========================================
# SMART LEARNING & TIMESTAMPED NOTES
# ==========================================

@login_required
def add_lesson_note(request, course_slug, lesson_slug):
    """Allows students to save timestamped personal notes during video lessons."""
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)

    if request.method == 'POST':
        note_text = request.POST.get('note_text', '').strip()
        timestamp_seconds = int(request.POST.get('timestamp_seconds', 0) or 0)

        if note_text:
            note = LessonNote.objects.create(
                user=request.user,
                lesson=lesson,
                timestamp_seconds=timestamp_seconds,
                note_text=note_text
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
                return JsonResponse({
                    'success': True,
                    'id': note.id,
                    'timestamp_display': note.timestamp_display,
                    'timestamp_seconds': note.timestamp_seconds,
                    'note_text': note.note_text,
                    'created_at': note.created_at.strftime('%b %d, %Y %H:%M')
                })
            messages.success(request, f"Note added at {note.timestamp_display}!")
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
                return JsonResponse({'success': False, 'error': 'Note text cannot be empty'})
            messages.error(request, "Note text cannot be empty.")

    return redirect('courses:lesson_detail', course_slug=course.slug, lesson_slug=lesson.slug)


@login_required
def delete_lesson_note(request, note_id):
    note = get_object_or_404(LessonNote, id=note_id, user=request.user)
    course_slug = note.lesson.course.slug
    lesson_slug = note.lesson.slug
    note.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({'success': True})
    messages.info(request, "Note deleted.")
    return redirect('courses:lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)


# ==========================================
# AI QUIZ GENERATOR (Instructor / Admin)
# ==========================================

@login_required
def ai_quiz_generator(request):
    """Retired AI Quiz Generator endpoint - redirects cleanly to course catalog."""
    messages.info(request, "The AI quiz generator has been retired in favor of curated course lessons and practice sets.")
    return redirect('courses:course_list')


