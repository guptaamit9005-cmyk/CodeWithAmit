from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import (
    Course, CourseCategory, Lesson, Quiz, QuizQuestion,
    Enrollment, LessonProgress, CourseBookmark, CourseReview, LessonNote
)
from .forms import CourseForm, LessonForm, QuizQuestionForm, CourseCategoryForm
from .ai_quiz_service import generate_mcq_quiz


def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('category', 'instructor')
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
    lessons = course.lessons.all().order_by('order')
    reviews = course.reviews.select_related('user').order_by('-created_at')[:10]

    is_enrolled = False
    is_bookmarked = False
    user_progress = 0

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
        is_bookmarked = CourseBookmark.objects.filter(user=request.user, course=course).exists()
        user_progress = course.get_progress_for_user(request.user)

    context = {
        'course': course,
        'lessons': lessons,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'is_bookmarked': is_bookmarked,
        'user_progress': user_progress,
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
    lessons = list(course.lessons.all().order_by('order'))

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

    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
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
    initial_data = {}
    selected_course = None
    if course_slug:
        selected_course = Course.objects.filter(slug=course_slug).first()
        if selected_course:
            initial_data['course'] = selected_course.pk
            initial_data['order'] = selected_course.lessons.count() + 1

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
    """
    AI-powered tool for instructors and admins to generate multiple choice quiz questions
    from lesson content or custom topics and automatically add them to lesson quizzes.
    """
    if not (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only instructors or platform admins can use the AI Quiz Generator.")
        return redirect('courses:course_list')

    courses = Course.objects.all().prefetch_related('lessons')
    selected_lesson_id = request.GET.get('lesson') or request.POST.get('lesson')
    selected_lesson = None
    if selected_lesson_id:
        selected_lesson = Lesson.objects.filter(id=selected_lesson_id).first()

    generated_questions = []
    topic_or_content = ""
    num_questions = 5
    difficulty = "Intermediate"

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'generate':
            topic_or_content = request.POST.get('topic_or_content', '').strip()
            num_questions = int(request.POST.get('num_questions', 5))
            difficulty = request.POST.get('difficulty', 'Intermediate')

            # If content is empty but a lesson is selected, load lesson content
            if not topic_or_content and selected_lesson:
                topic_or_content = f"Title: {selected_lesson.title}\nContent: {selected_lesson.content}"

            if topic_or_content:
                generated_questions = generate_mcq_quiz(
                    topic_or_content=topic_or_content,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
                messages.success(request, f"✨ Successfully generated {len(generated_questions)} AI quiz questions! Review and save below.")
            else:
                messages.error(request, "Please enter a topic or select a lesson to generate questions.")

        elif action == 'save_quiz':
            lesson_id = request.POST.get('target_lesson_id')
            lesson = get_object_or_404(Lesson, id=lesson_id)
            quiz, _ = Quiz.objects.get_or_create(
                lesson=lesson,
                defaults={'title': f"Quiz: {lesson.title}", 'passing_score': 70}
            )

            # Extract submitted questions
            q_count = int(request.POST.get('total_generated_count', 0))
            saved_count = 0
            for i in range(1, q_count + 1):
                q_text = request.POST.get(f'q_text_{i}', '').strip()
                opt_a = request.POST.get(f'opt_a_{i}', '').strip()
                opt_b = request.POST.get(f'opt_b_{i}', '').strip()
                opt_c = request.POST.get(f'opt_c_{i}', '').strip()
                opt_d = request.POST.get(f'opt_d_{i}', '').strip()
                correct = request.POST.get(f'correct_{i}', 'A').strip().upper()
                exp = request.POST.get(f'exp_{i}', '').strip()

                if q_text and opt_a and opt_b:
                    QuizQuestion.objects.create(
                        quiz=quiz,
                        question_text=q_text,
                        option_a=opt_a,
                        option_b=opt_b,
                        option_c=opt_c,
                        option_d=opt_d,
                        correct_option=correct,
                        explanation=exp
                    )
                    saved_count += 1

            messages.success(request, f"🎉 {saved_count} AI Questions saved and published to lesson '{lesson.title}' quiz!")
            return redirect('courses:lesson_detail', course_slug=lesson.course.slug, lesson_slug=lesson.slug)

    context = {
        'courses': courses,
        'selected_lesson': selected_lesson,
        'generated_questions': generated_questions,
        'topic_or_content': topic_or_content,
        'num_questions': num_questions,
        'difficulty': difficulty,
    }
    return render(request, 'courses/ai_quiz_generator.html', context)


