from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from judgy.decorators import verified_required
from notifications.models import TeamInviteNotification, Notification
from competitions.utils import team_add_user

@verified_required
def team_invite_accept_view(request, id):
    notification = get_object_or_404(TeamInviteNotification, id=id, user=request.user)
    team = notification.team
    competition = team.competition

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        for member in team.members.all():
            Notification.objects.create(
                user=member,
                header='Update',
                body=f'{request.user} has accepted the invitation to join the team.'
            )
        team_add_user(competition, team, request.user)
        notification.delete()
        return JsonResponse({})
