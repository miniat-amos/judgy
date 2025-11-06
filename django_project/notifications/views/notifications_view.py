from django.http import JsonResponse
from judgy.decorators import verified_required
from notifications.models import Notification

@verified_required
def notifications_view(request):
    return JsonResponse(list(Notification.objects.filter(user=request.user).values().order_by('-id')), safe=False)