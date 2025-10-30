from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..decorators import verified_required
from ..models import Competition, Team
from notifications.models import Notification

@verified_required
def team_leave_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        team = Team.objects.filter(competition=competition, members=request.user).first()
        if team:
            team.members.remove(request.user)
            if team.members.count():
                for member in team.members.all():
                    Notification.objects.create(
                        user=member,
                        header='Update',
                        body=f'{request.user} left the team.'
                    )
            else:
                team.delete()
            return JsonResponse({})
