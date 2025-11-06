from django.shortcuts import render
from judgy.decorators import verified_required

@verified_required
def notification_center_view(request):
    return render(request, "notifications/notification_center.html")
    