from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ..decorators import verified_required
from ..models import TeamJoinNotification, Notification

@verified_required
def team_join_decline_view(request, id):
    notification = get_object_or_404(TeamJoinNotification, id=id, user=request.user)
    team = notification.team
    competition = team.competition

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        for member in team.members.all():
            if member != request.user:
                Notification.objects.create(
                    user=member,
                    header='Update',
                    body=f'{request.user} has declined the request of {notification.request_user} to join the team.'
                )
        Notification.objects.create(
            user=notification.request_user,
            header='Update',
            body=f'"{team.name}" has declined your request to join the team.'
        )
        TeamJoinNotification.objects.filter(request_user=notification.request_user, team=team).delete()
        return JsonResponse({})
