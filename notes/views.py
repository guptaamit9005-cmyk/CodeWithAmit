from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.db.models import F
from .models import Note, NoteCategory, NoteBookmark
from .forms import NoteUploadForm

def note_list(request):
    notes = Note.objects.filter(is_approved=True).select_related('category', 'uploader')
    categories = NoteCategory.objects.all()

    category_slug = request.GET.get('category')
    semester = request.GET.get('semester')
    language = request.GET.get('language')
    query = request.GET.get('q')

    if category_slug:
        notes = notes.filter(category__slug=category_slug)
    if semester and semester != 'all':
        notes = notes.filter(semester=semester)
    if language:
        notes = notes.filter(programming_language__icontains=language)
    if query:
        notes = notes.filter(title__icontains=query)

    context = {
        'notes': notes,
        'categories': categories,
        'selected_category': category_slug,
        'selected_semester': semester,
        'selected_language': language,
        'query': query,
        'semester_choices': Note.SEMESTER_CHOICES,
    }
    return render(request, 'notes/note_list.html', context)


def note_detail(request, slug):
    note = get_object_or_404(Note, slug=slug, is_approved=True)
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = NoteBookmark.objects.filter(user=request.user, note=note).exists()

    related_notes = Note.objects.filter(category=note.category, is_approved=True).exclude(pk=note.pk)[:4]

    context = {
        'note': note,
        'is_bookmarked': is_bookmarked,
        'related_notes': related_notes,
    }
    return render(request, 'notes/note_detail.html', context)


@login_required
def upload_note(request):
    if request.method == 'POST':
        form = NoteUploadForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.uploader = request.user
            # Auto-approve for demo/testing so users immediately see their uploads
            note.is_approved = True
            note.save()
            messages.success(request, f"Note '{note.title}' uploaded successfully!")
            return redirect('notes:note_detail', slug=note.slug)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = NoteUploadForm()

    return render(request, 'notes/upload_note.html', {'form': form})


def download_note(request, slug):
    note = get_object_or_404(Note, slug=slug, is_approved=True)
    if not note.file:
        messages.warning(request, "This sample note preview is available online below. Complete PDF file will be available soon.")
        return redirect('notes:note_detail', slug=slug)

    # Increment download count
    Note.objects.filter(pk=note.pk).update(download_count=F('download_count') + 1)
    return FileResponse(note.file.open('rb'), as_attachment=True, filename=note.file.name.split('/')[-1])


@login_required
def toggle_bookmark(request, slug):
    note = get_object_or_404(Note, slug=slug)
    bookmark = NoteBookmark.objects.filter(user=request.user, note=note)
    if bookmark.exists():
        bookmark.delete()
        messages.info(request, "Removed note from bookmarks.")
    else:
        NoteBookmark.objects.create(user=request.user, note=note)
        messages.success(request, "Note saved to your bookmarks.")
    return redirect('notes:note_detail', slug=slug)


@login_required
def edit_note(request, slug):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can edit notes.")
        return redirect('notes:note_list')

    note = get_object_or_404(Note, slug=slug)
    if request.method == 'POST':
        form = NoteUploadForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, f"Note '{note.title}' updated successfully!")
            return redirect('notes:note_detail', slug=note.slug)
    else:
        form = NoteUploadForm(instance=note)

    return render(request, 'notes/upload_note.html', {'form': form, 'is_edit': True, 'note': note})


@login_required
def delete_note(request, slug):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Only administrators can delete notes.")
        return redirect('notes:note_list')

    note = get_object_or_404(Note, slug=slug)
    if request.method == 'POST':
        title = note.title
        note.delete()
        messages.success(request, f"Note '{title}' has been deleted.")
        return redirect('dashboard:admin_dashboard')

    return render(request, 'notes/note_confirm_delete.html', {'note': note})

