from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from judgy.decorators import verified_required
from notifications.models import TeamJoinNotification, Notification
from judgy.utils import team_add_user

@verified_required
def team_join_accept_view(request, id):
    notification = get_object_or_404(TeamJoinNotification, id=id, user=request.user)
    team = notification.team
    competition = team.competition

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        for member in team.members.all():
            if member != request.user:
                Notification.objects.create(
                    user=member,
                    header='Update',
                    body=f'{request.user} has accepted the request of {notification.request_user} to join the team.'
                )
        Notification.objects.create(
            user=notification.request_user,
            header='Update',
            body=f'"{team.name}" has accepted your request to join the team.'
        )
        team_add_user(competition, team, notification.request_user)
        TeamJoinNotification.objects.filter(request_user=notification.request_user, team=team).delete()
        return JsonResponse({})
