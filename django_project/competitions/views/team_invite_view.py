from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from judgy.decorators import verified_required
from competitions.forms import TeamInviteForm
from competitions.models import Competition, Team, User
from notifications.models import TeamInviteNotification

@verified_required
def team_invite_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == 'POST':
        if competition.enroll_start <= timezone.now() < competition.enroll_end:
            team = Team.objects.filter(competition=competition, members=request.user).first()
            team_invite_limit = competition.team_size_limit - (team.members.count() if team else 0)
            form = TeamInviteForm(data=request.POST, team_invite_limit=team_invite_limit)
            if form.is_valid():
                for field in form.fields:
                    email = form.cleaned_data[field]
                    if email:
                        user = User.objects.filter(email=email).first()
                        if user:
                            body = f'Hi {user.first_name}, {request.user} has invited you to join the team "{team.name}" for the competition "{competition.name}".'
                            TeamInviteNotification.objects.create(user=user, body=body, team=team)
                return redirect('competitions:team_name', code=team.competition.code, name=team.name)
            else:
                print('Some field was incorrectly filled out.')
                print('form.errors:\n', form.errors)
