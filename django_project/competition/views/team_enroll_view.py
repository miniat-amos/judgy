from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from judgy.decorators import verified_required
from competition.forms import TeamEnrollForm
from competition.models import Competition, Team
from notifications.models import TeamJoinNotification
from competition.utils import team_add_user

@verified_required
def team_enroll_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == 'POST':
        if competition.enroll_start <= timezone.now() < competition.enroll_end:
            form = TeamEnrollForm(data=request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name')
                team, created = Team.objects.get_or_create(
                    competition=competition,
                    name=name
                )
                if created:
                    team_add_user(competition, team, request.user)
                else:
                    for member in team.members.all():
                        user = member
                        body = f'Hi {member.first_name}, {request.user} wants to join your team "{team.name}" for the competition "{competition.name}".'
                        TeamJoinNotification.objects.create(user=user, body=body, request_user=request.user, team=team)
                return redirect('competition:team_name', code=team.competition.code, name=team.name)
            else:
                print('Some field was not correctly filled.')
                print('form.errors:\n', form.errors)
