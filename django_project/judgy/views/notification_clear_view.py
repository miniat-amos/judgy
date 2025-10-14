

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..decorators import verified_required
from ..models import Notification

@verified_required
def notification_clear_view(request, id):
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.delete()
    return JsonResponse({})