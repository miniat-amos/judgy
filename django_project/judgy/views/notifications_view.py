

from django.http import JsonResponse
from ..decorators import verified_required
from ..models import Notification

@verified_required
def notifications_view(request):
    return JsonResponse(list(Notification.objects.filter(user=request.user).values()), safe=False)