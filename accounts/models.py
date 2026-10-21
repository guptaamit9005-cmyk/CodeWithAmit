from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Platform Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    headline = models.CharField(max_length=150, blank=True, help_text="e.g. Aspiring Full-Stack Developer | CS Sophomore")
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    target_career = models.CharField(max_length=100, blank=True, help_text="e.g. AI/ML Engineer, SDE-1")
    
    # Gamification and Streaks
    points = models.PositiveIntegerField(default=100)
    streak_count = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_instructor(self):
        return self.role in ('instructor', 'admin') or self.user.is_staff

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.user.is_superuser

    def update_streak(self):
        today = timezone.now().date()
        if self.last_active_date is None:
            self.streak_count = 1
            self.last_active_date = today
            self.save(update_fields=['streak_count', 'last_active_date'])
        elif self.last_active_date == today:
            # Already active today
            pass
        elif self.last_active_date == today - timedelta(days=1):
            self.streak_count += 1
            self.last_active_date = today
            self.save(update_fields=['streak_count', 'last_active_date'])
        else:
            # Missed a day
            self.streak_count = 1
            self.last_active_date = today
            self.save(update_fields=['streak_count', 'last_active_date'])

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='bi-award-fill', help_text="Bootstrap icon class")
    color = models.CharField(max_length=30, default='primary', help_text="e.g. primary, warning, success, danger, info, purple")
    category = models.CharField(max_length=50, default='DSA', help_text="e.g. Streak, DSA, Contest, Community")
    points_reward = models.PositiveIntegerField(default=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_users')
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"


def check_and_award_badges(user):
    """
    Evaluates student stats and awards relevant badges automatically.
    Returns list of newly awarded badge objects.
    """
    if not user.is_authenticated:
        return []

    newly_awarded = []
    profile = getattr(user, 'profile', None)
    if not profile:
        return []

    # Ensure standard badges exist
    default_badges = [
        ('platform-pioneer', 'Platform Pioneer', 'Joined Codestyle and started the journey', 'bi-mortarboard-fill', 'info', 'General', 20),
        ('streak-3', 'Consistency Builder', 'Maintained a 3-day coding streak', 'bi-fire', 'warning', 'Streak', 50),
        ('streak-7', '7-Day Streak Master', 'Unstoppable! Maintained a 7-day coding streak', 'bi-lightning-charge-fill', 'danger', 'Streak', 100),
        ('dsa-explorer', 'DSA Explorer', 'Solved your first DSA problem', 'bi-code-slash', 'success', 'DSA', 30),
        ('dsa-solver', 'Algorithm Achiever', 'Solved 5 or more coding problems', 'bi-cpu-fill', 'primary', 'DSA', 80),
        ('dsa-master', 'DSA Grandmaster', 'Mastered 10 or more coding problems', 'bi-trophy-fill', 'warning', 'DSA', 200),
        ('potd-warrior', 'POTD Champion', 'Solved the Problem of the Day challenge', 'bi-stars', 'info', 'POTD', 50),
        ('contest-hero', 'Contest Contender', 'Registered and competed in a weekly contest', 'bi-flag-fill', 'purple', 'Contest', 100),
        ('community-helper', 'Doubt Solver', 'Participated in discussions or solved peer doubts', 'bi-chat-heart-fill', 'success', 'Community', 60),
    ]

    for slug, name, desc, icon, color, cat, pts in default_badges:
        Badge.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': desc,
                'icon': icon,
                'color': color,
                'category': cat,
                'points_reward': pts,
            }
        )

    # 1. Pioneer badge (always awarded)
    pioneer = Badge.objects.filter(slug='platform-pioneer').first()
    if pioneer and not UserBadge.objects.filter(user=user, badge=pioneer).exists():
        UserBadge.objects.create(user=user, badge=pioneer)
        newly_awarded.append(pioneer)

    # 2. Streak badges
    if profile.streak_count >= 3:
        b = Badge.objects.filter(slug='streak-3').first()
        if b and not UserBadge.objects.filter(user=user, badge=b).exists():
            UserBadge.objects.create(user=user, badge=b)
            profile.points += b.points_reward
            newly_awarded.append(b)

    if profile.streak_count >= 7:
        b = Badge.objects.filter(slug='streak-7').first()
        if b and not UserBadge.objects.filter(user=user, badge=b).exists():
            UserBadge.objects.create(user=user, badge=b)
            profile.points += b.points_reward
            newly_awarded.append(b)

    # 3. DSA Solved badges
    from coding_practice.models import UserQuestionStatus
    solved_count = UserQuestionStatus.objects.filter(user=user, status='solved').count()

    if solved_count >= 1:
        b = Badge.objects.filter(slug='dsa-explorer').first()
        if b and not UserBadge.objects.filter(user=user, badge=b).exists():
            UserBadge.objects.create(user=user, badge=b)
            profile.points += b.points_reward
            newly_awarded.append(b)

    if solved_count >= 5:
        b = Badge.objects.filter(slug='dsa-solver').first()
        if b and not UserBadge.objects.filter(user=user, badge=b).exists():
            UserBadge.objects.create(user=user, badge=b)
            profile.points += b.points_reward
            newly_awarded.append(b)

    if solved_count >= 10:
        b = Badge.objects.filter(slug='dsa-master').first()
        if b and not UserBadge.objects.filter(user=user, badge=b).exists():
            UserBadge.objects.create(user=user, badge=b)
            profile.points += b.points_reward
            newly_awarded.append(b)

    if newly_awarded:
        profile.save(update_fields=['points'])

    return newly_awarded

