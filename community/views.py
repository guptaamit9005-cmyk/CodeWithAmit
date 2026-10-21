from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from .models import DoubtQuestion, DoubtAnswer, DoubtTag
from .forms import DoubtQuestionForm, DoubtAnswerForm
from accounts.models import check_and_award_badges

def doubt_list(request):
    """StackOverflow-style doubt and Q&A community feed with tag and filter controls."""
    questions = DoubtQuestion.objects.all().select_related('author', 'author__profile').prefetch_related('tags', 'answers', 'upvotes')

    filter_type = request.GET.get('filter', 'all')
    tag_slug = request.GET.get('tag')
    query = request.GET.get('q', '').strip()

    if tag_slug:
        questions = questions.filter(tags__slug=tag_slug)

    if query:
        questions = questions.filter(
            Q(title__icontains=query) | Q(body__icontains=query) | Q(raw_tags__icontains=query)
        )

    if filter_type == 'unanswered':
        questions = questions.annotate(ans_count=Count('answers')).filter(ans_count=0)
    elif filter_type == 'solved':
        questions = questions.filter(has_accepted_answer=True)
    elif filter_type == 'my_doubts' and request.user.is_authenticated:
        questions = questions.filter(author=request.user)

    # Seed demo doubts if empty
    if not DoubtQuestion.objects.exists():
        from django.contrib.auth.models import User
        demo_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if demo_user:
            d1 = DoubtQuestion.objects.create(
                author=demo_user,
                title="How to optimize Time Complexity from O(N^2) to O(N) in Two Sum?",
                body="I was solving the Two Sum problem using nested loops which takes O(N^2) time. How can I use a HashMap or Python dictionary to achieve linear O(N) runtime?",
                code_snippet="def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]",
                language="python",
                raw_tags="python, dsa, hashmap, algorithms",
                has_accepted_answer=True
            )
            DoubtAnswer.objects.create(
                question=d1,
                author=demo_user,
                body="You can maintain a dictionary storing `num -> index`. For each number `x`, check if `target - x` is already in the map. If yes, return both indices in a single pass!",
                code_snippet="def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []",
                is_accepted=True
            )

            DoubtQuestion.objects.create(
                author=demo_user,
                title="Difference between Recursion and Dynamic Programming with Memoization?",
                body="When should I use pure recursion versus storing subproblem results in a memo table (top-down DP)? Does memoization always eliminate stack overflow?",
                language="general",
                raw_tags="dsa, dynamic-programming, recursion"
            )
            questions = DoubtQuestion.objects.all().select_related('author', 'author__profile')

    # Popular tags
    popular_tags = DoubtTag.objects.annotate(q_count=Count('questions')).order_by('-q_count')[:10]

    return render(request, 'community/doubt_list.html', {
        'questions': questions,
        'filter_type': filter_type,
        'selected_tag': tag_slug,
        'query': query,
        'popular_tags': popular_tags,
        'total_doubts': DoubtQuestion.objects.count(),
        'solved_doubts': DoubtQuestion.objects.filter(has_accepted_answer=True).count(),
    })


def doubt_detail(request, slug):
    question = get_object_or_404(DoubtQuestion.objects.select_related('author', 'author__profile'), slug=slug)
    
    # Increment views
    question.views_count += 1
    question.save(update_fields=['views_count'])

    answers = question.answers.select_related('author', 'author__profile').prefetch_related('upvotes').order_by('-is_accepted', '-created_at')
    answer_form = DoubtAnswerForm()

    user_has_upvoted = False
    if request.user.is_authenticated:
        user_has_upvoted = question.upvotes.filter(id=request.user.id).exists()

    return render(request, 'community/doubt_detail.html', {
        'question': question,
        'answers': answers,
        'answer_form': answer_form,
        'user_has_upvoted': user_has_upvoted,
        'is_author': (request.user == question.author),
    })


@login_required
def ask_doubt(request):
    if request.method == 'POST':
        form = DoubtQuestionForm(request.POST)
        if form.is_valid():
            doubt = form.save(commit=False)
            doubt.author = request.user
            doubt.save()

            # Process tags
            if doubt.raw_tags:
                tag_names = [t.strip().lower() for t in doubt.raw_tags.split(',') if t.strip()]
                for t_name in tag_names:
                    tag_obj, _ = DoubtTag.objects.get_or_create(name=t_name)
                    doubt.tags.add(tag_obj)

            # Reward asking
            if hasattr(request.user, 'profile'):
                request.user.profile.points += 15
                request.user.profile.save(update_fields=['points'])
            check_and_award_badges(request.user)

            messages.success(request, f"🎉 Your question '{doubt.title}' is now live on the Doubt Forum (+15 XP)!")
            return redirect('community:doubt_detail', slug=doubt.slug)
    else:
        form = DoubtQuestionForm()

    return render(request, 'community/ask_doubt.html', {'form': form})


@login_required
def post_answer(request, slug):
    question = get_object_or_404(DoubtQuestion, slug=slug)
    if request.method == 'POST':
        form = DoubtAnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()

            # Reward answering
            if hasattr(request.user, 'profile'):
                request.user.profile.points += 25
                request.user.profile.save(update_fields=['points'])
            check_and_award_badges(request.user)

            messages.success(request, "🎉 Your answer has been submitted (+25 XP)!")
        else:
            messages.error(request, "Please enter a valid answer body.")

    return redirect('community:doubt_detail', slug=question.slug)


@login_required
def toggle_question_upvote(request, question_id):
    question = get_object_or_404(DoubtQuestion, id=question_id)
    if request.user in question.upvotes.all():
        question.upvotes.remove(request.user)
        upvoted = False
    else:
        question.upvotes.add(request.user)
        upvoted = True
        if hasattr(question.author, 'profile'):
            question.author.profile.points += 5
            question.author.profile.save(update_fields=['points'])

    return JsonResponse({
        'success': True,
        'upvoted': upvoted,
        'total_upvotes': question.total_upvotes
    })


@login_required
def toggle_answer_upvote(request, answer_id):
    answer = get_object_or_404(DoubtAnswer, id=answer_id)
    if request.user in answer.upvotes.all():
        answer.upvotes.remove(request.user)
        upvoted = False
    else:
        answer.upvotes.add(request.user)
        upvoted = True
        if hasattr(answer.author, 'profile'):
            answer.author.profile.points += 5
            answer.author.profile.save(update_fields=['points'])

    return JsonResponse({
        'success': True,
        'upvoted': upvoted,
        'total_upvotes': answer.total_upvotes
    })


@login_required
def accept_answer(request, answer_id):
    answer = get_object_or_404(DoubtAnswer, id=answer_id)
    question = answer.question

    if request.user != question.author and not request.user.is_staff:
        messages.error(request, "Only the author of this question can mark an accepted answer.")
        return redirect('community:doubt_detail', slug=question.slug)

    # Unmark any existing accepted answer for this question
    question.answers.update(is_accepted=False)
    answer.is_accepted = True
    answer.save(update_fields=['is_accepted'])

    question.has_accepted_answer = True
    question.save(update_fields=['has_accepted_answer'])

    # Reward responder with bonus +50 XP
    if hasattr(answer.author, 'profile'):
        answer.author.profile.points += 50
        answer.author.profile.save(update_fields=['points'])
        check_and_award_badges(answer.author)

    messages.success(request, f"✨ Marked {answer.author.username}'s answer as the Accepted Solution (+50 XP bonus awarded)!")
    return redirect('community:doubt_detail', slug=question.slug)
