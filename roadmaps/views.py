import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from courses.models import Course
from coding_practice.models import CodingQuestion
from notes.models import Note
from .models import Roadmap, RoadmapStage, RoadmapTopic, UserRoadmapEnrollment, UserTopicProgress
from .forms import RoadmapForm, RoadmapStageForm, RoadmapTopicForm


def roadmap_list(request):
    roadmaps = Roadmap.objects.filter(is_published=True).prefetch_related('stages__topics')
    
    # Calculate user progress per roadmap if logged in
    user_progress_map = {}
    enrolled_roadmap_ids = set()
    if request.user.is_authenticated:
        enrolled_roadmap_ids = set(
            UserRoadmapEnrollment.objects.filter(user=request.user).values_list('roadmap_id', flat=True)
        )
        for r in roadmaps:
            user_progress_map[r.id] = r.get_user_completion_percent(request.user)

    for r in roadmaps:
        r.user_progress = user_progress_map.get(r.id, 0)
        r.is_enrolled = (r.id in enrolled_roadmap_ids)

    # Feature counts for Dashboard Launcher
    courses_count = Course.objects.count()
    questions_count = CodingQuestion.objects.count()
    notes_count = Note.objects.count()
    sample_question = CodingQuestion.objects.first()

    context = {
        'roadmaps': roadmaps,
        'courses_count': courses_count,
        'questions_count': questions_count,
        'notes_count': notes_count,
        'sample_question': sample_question,
    }
    return render(request, 'roadmaps/roadmap_list.html', context)


def roadmap_detail(request, slug):
    roadmap = get_object_or_404(Roadmap, slug=slug, is_published=True)
    stages = roadmap.stages.prefetch_related(
        'topics__related_course',
        'topics__related_note',
        'topics__related_question'
    ).order_by('order')

    is_enrolled = False
    completed_topic_ids = set()
    completion_percent = 0

    if request.user.is_authenticated:
        is_enrolled = UserRoadmapEnrollment.objects.filter(user=request.user, roadmap=roadmap).exists()
        completed_topic_ids = set(
            UserTopicProgress.objects.filter(
                user=request.user,
                topic__stage__roadmap=roadmap,
                is_completed=True
            ).values_list('topic_id', flat=True)
        )
        completion_percent = roadmap.get_user_completion_percent(request.user)

    context = {
        'roadmap': roadmap,
        'stages': stages,
        'is_enrolled': is_enrolled,
        'completed_topic_ids': completed_topic_ids,
        'completion_percent': completion_percent,
    }
    return render(request, 'roadmaps/roadmap_detail.html', context)


@login_required
def enroll_roadmap(request, slug):
    roadmap = get_object_or_404(Roadmap, slug=slug, is_published=True)
    enrollment, created = UserRoadmapEnrollment.objects.get_or_create(user=request.user, roadmap=roadmap)
    if created:
        messages.success(request, f"Enrolled in the '{roadmap.title}' career roadmap! Check off topics as you learn.")
    else:
        messages.info(request, f"You are already following '{roadmap.title}'.")
    return redirect('roadmaps:roadmap_detail', slug=roadmap.slug)


@login_required
def toggle_topic_progress(request, slug, topic_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    roadmap = get_object_or_404(Roadmap, slug=slug)
    topic = get_object_or_404(RoadmapTopic, id=topic_id, stage__roadmap=roadmap)

    # Auto enroll if not already
    UserRoadmapEnrollment.objects.get_or_create(user=request.user, roadmap=roadmap)

    progress, _ = UserTopicProgress.objects.get_or_create(user=request.user, topic=topic)

    try:
        data = json.loads(request.body)
        is_completed = data.get('is_completed', not progress.is_completed)
    except Exception:
        is_completed = not progress.is_completed

    progress.is_completed = is_completed
    progress.completed_at = timezone.now() if is_completed else None
    progress.save()

    new_percent = roadmap.get_user_completion_percent(request.user)

    return JsonResponse({
        'success': True,
        'is_completed': progress.is_completed,
        'completion_percent': new_percent,
    })


@login_required
def create_roadmap(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can create career roadmaps.")
        return redirect('roadmaps:roadmap_list')

    if request.method == 'POST':
        form = RoadmapForm(request.POST)
        if form.is_valid():
            roadmap = form.save()
            messages.success(request, f"Roadmap '{roadmap.title}' created and published live! It is now visible to all users.")
            return redirect('roadmaps:roadmap_detail', slug=roadmap.slug)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RoadmapForm(initial={'is_published': True, 'banner_color': 'linear-gradient(135deg, #2563eb, #06b6d4)'})

    return render(request, 'roadmaps/roadmap_form.html', {'form': form})


@login_required
def edit_roadmap(request, slug):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can edit roadmaps.")
        return redirect('roadmaps:roadmap_list')

    roadmap = get_object_or_404(Roadmap, slug=slug)
    if request.method == 'POST':
        form = RoadmapForm(request.POST, instance=roadmap)
        if form.is_valid():
            form.save()
            messages.success(request, f"Roadmap '{roadmap.title}' updated successfully!")
            return redirect('roadmaps:roadmap_detail', slug=roadmap.slug)
    else:
        form = RoadmapForm(instance=roadmap)

    return render(request, 'roadmaps/roadmap_form.html', {'form': form, 'is_edit': True, 'roadmap': roadmap})


@login_required
def delete_roadmap(request, slug):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can delete roadmaps.")
        return redirect('roadmaps:roadmap_list')

    roadmap = get_object_or_404(Roadmap, slug=slug)
    if request.method == 'POST':
        title = roadmap.title
        roadmap.delete()
        messages.success(request, f"Roadmap '{title}' has been deleted.")
        return redirect('roadmaps:roadmap_list')

    return render(request, 'roadmaps/roadmap_confirm_delete.html', {'roadmap': roadmap})


@login_required
def add_stage(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can add roadmap stages.")
        return redirect('roadmaps:roadmap_list')

    roadmap_slug = request.GET.get('roadmap')
    initial_data = {}
    if roadmap_slug:
        rm = Roadmap.objects.filter(slug=roadmap_slug).first()
        if rm:
            initial_data['roadmap'] = rm.pk
            initial_data['order'] = rm.stages.count() + 1

    if request.method == 'POST':
        form = RoadmapStageForm(request.POST)
        if form.is_valid():
            stage = form.save()
            messages.success(request, f"Stage '{stage.title}' added to roadmap '{stage.roadmap.title}'!")
            return redirect('roadmaps:roadmap_detail', slug=stage.roadmap.slug)
    else:
        form = RoadmapStageForm(initial=initial_data)

    return render(request, 'roadmaps/stage_form.html', {'form': form, 'roadmap_slug': roadmap_slug})


@login_required
def edit_stage(request, stage_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can edit roadmap stages.")
        return redirect('roadmaps:roadmap_list')

    stage = get_object_or_404(RoadmapStage, pk=stage_id)
    if request.method == 'POST':
        form = RoadmapStageForm(request.POST, instance=stage)
        if form.is_valid():
            form.save()
            messages.success(request, f"Stage '{stage.title}' updated successfully!")
            return redirect('roadmaps:roadmap_detail', slug=stage.roadmap.slug)
    else:
        form = RoadmapStageForm(instance=stage)

    return render(request, 'roadmaps/stage_form.html', {'form': form, 'stage': stage, 'is_edit': True, 'roadmap_slug': stage.roadmap.slug})


@login_required
def delete_stage(request, stage_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can delete roadmap stages.")
        return redirect('roadmaps:roadmap_list')

    stage = get_object_or_404(RoadmapStage, pk=stage_id)
    roadmap_slug = stage.roadmap.slug
    title = stage.title
    stage.delete()
    messages.success(request, f"Stage '{title}' deleted.")
    return redirect('roadmaps:roadmap_detail', slug=roadmap_slug)


@login_required
def add_topic(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can add roadmap topics.")
        return redirect('roadmaps:roadmap_list')

    stage_id = request.GET.get('stage')
    initial_data = {}
    stage = None
    if stage_id:
        st = RoadmapStage.objects.filter(pk=stage_id).first()
        if st:
            stage = st
            initial_data['stage'] = st.pk
            initial_data['order'] = st.topics.count() + 1

    if request.method == 'POST':
        form = RoadmapTopicForm(request.POST)
        if form.is_valid():
            topic = form.save()
            messages.success(request, f"Topic '{topic.title}' added to stage '{topic.stage.title}'!")
            return redirect('roadmaps:roadmap_detail', slug=topic.stage.roadmap.slug)
    else:
        form = RoadmapTopicForm(initial=initial_data)

    return render(request, 'roadmaps/topic_form.html', {'form': form, 'stage': stage})


@login_required
def edit_topic(request, topic_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can edit roadmap topics.")
        return redirect('roadmaps:roadmap_list')

    topic = get_object_or_404(RoadmapTopic, pk=topic_id)
    if request.method == 'POST':
        form = RoadmapTopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, f"Topic '{topic.title}' updated successfully!")
            return redirect('roadmaps:roadmap_detail', slug=topic.stage.roadmap.slug)
    else:
        form = RoadmapTopicForm(instance=topic)

    return render(request, 'roadmaps/topic_form.html', {'form': form, 'topic': topic, 'is_edit': True, 'stage': topic.stage})


@login_required
def delete_topic(request, topic_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can delete roadmap topics.")
        return redirect('roadmaps:roadmap_list')

    topic = get_object_or_404(RoadmapTopic, pk=topic_id)
    roadmap_slug = topic.stage.roadmap.slug
    title = topic.title
    topic.delete()
    messages.success(request, f"Topic '{title}' deleted.")
    return redirect('roadmaps:roadmap_detail', slug=roadmap_slug)

