from .views import base_notifications

def notifications_processor(request):
    if request.user.is_authenticated:
        return base_notifications(request)
    return {"notifications": [], "unread_count": 0}
