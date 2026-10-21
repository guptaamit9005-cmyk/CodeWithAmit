from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify
from .models import LiveClass, ClassAttendee
from .forms import LiveClassScheduleForm
from notifications.models import Notification

def class_list(request):
    classes = LiveClass.objects.all().select_related('instructor')
    status_filter = request.GET.get('status')
    
    if status_filter:
        classes = classes.filter(status=status_filter)
        
    upcoming_classes = LiveClass.objects.filter(status='upcoming')
    live_classes = LiveClass.objects.filter(status='live')
    completed_classes = LiveClass.objects.filter(status='completed')

    registered_class_ids = set()
    if request.user.is_authenticated:
        registered_class_ids = set(
            ClassAttendee.objects.filter(user=request.user).values_list('live_class_id', flat=True)
        )

    context = {
        'classes': classes,
        'upcoming_classes': upcoming_classes,
        'live_classes': live_classes,
        'completed_classes': completed_classes,
        'registered_class_ids': registered_class_ids,
        'status_filter': status_filter,
    }
    return render(request, 'live_classes/class_list.html', context)


def class_detail(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = ClassAttendee.objects.filter(user=request.user, live_class=live_class).exists()

    attendees = live_class.attendees.select_related('user').all()[:15]

    context = {
        'live_class': live_class,
        'is_registered': is_registered,
        'attendees': attendees,
    }
    return render(request, 'live_classes/class_detail.html', context)


@login_required
def register_class(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    attendee, created = ClassAttendee.objects.get_or_create(user=request.user, live_class=live_class)

    if created:
        Notification.objects.create(
            user=request.user,
            title="Class Registration Confirmed",
            message=f"You are registered for '{live_class.title}' on {live_class.scheduled_date} at {live_class.start_time}.",
            link_url=f"/live-classes/{live_class.pk}/",
            notification_type='class'
        )
        messages.success(request, f"Registered for '{live_class.title}'! Google Meet access is ready.")
    else:
        messages.info(request, "You are already registered for this live session.")

    return redirect('live_classes:class_detail', pk=live_class.pk)


@login_required
def join_class(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)
    attendee, _ = ClassAttendee.objects.get_or_create(user=request.user, live_class=live_class)
    attendee.has_joined = True
    attendee.joined_at = timezone.now()
    attendee.save()

    return redirect(live_class.google_meet_url)


@login_required
def create_class(request):
    if not (request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only instructors can schedule live classes.")
        return redirect('live_classes:class_list')

    if request.method == 'POST':
        form = LiveClassScheduleForm(request.POST, request.FILES)
        if form.is_valid():
            live_class = form.save(commit=False)
            live_class.instructor = request.user
            live_class.slug = slugify(live_class.title)
            live_class.save()

            messages.success(request, f"Live class '{live_class.title}' scheduled successfully!")
            return redirect('live_classes:class_detail', pk=live_class.pk)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = LiveClassScheduleForm()

    return render(request, 'live_classes/create_class.html', {'form': form})


@login_required
def edit_class(request, pk):
    if not (request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.is_instructor)):
        messages.error(request, "Only instructors or administrators can edit live classes.")
        return redirect('live_classes:class_list')

    live_class = get_object_or_404(LiveClass, pk=pk)
    if request.method == 'POST':
        form = LiveClassScheduleForm(request.POST, request.FILES, instance=live_class)
        if form.is_valid():
            form.save()
            messages.success(request, f"Live class '{live_class.title}' updated successfully!")
            return redirect('live_classes:class_detail', pk=live_class.pk)
    else:
        form = LiveClassScheduleForm(instance=live_class)

    return render(request, 'live_classes/create_class.html', {'form': form, 'is_edit': True, 'live_class': live_class})


@login_required
def delete_class(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can delete live classes.")
        return redirect('live_classes:class_list')

    live_class = get_object_or_404(LiveClass, pk=pk)
    if request.method == 'POST':
        title = live_class.title
        live_class.delete()
        messages.success(request, f"Live class '{title}' has been deleted.")
        return redirect('dashboard:admin_dashboard')

    return render(request, 'live_classes/class_confirm_delete.html', {'live_class': live_class})

