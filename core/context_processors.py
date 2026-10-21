from datetime import datetime

def global_context(request):
    """Provides common global context across all templates."""
    context = {
        'site_name': 'Student Success Hub',
        'current_year': datetime.now().year,
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }

    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            user_notifs = Notification.objects.filter(user=request.user)
            context['unread_notifications_count'] = user_notifs.filter(is_read=False).count()
            context['recent_notifications'] = user_notifs.order_by('-created_at')[:5]
        except Exception:
            pass

        try:
            from accounts.models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            context['user_profile'] = profile
        except Exception:
            pass

    return context
