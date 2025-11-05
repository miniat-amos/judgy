from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from competition.forms import CompetitionCreationForm, TeamEnrollForm, TeamInviteForm
from competition.models import Competition, Team

def team_name_view(request, code, name):
    competition = get_object_or_404(Competition, code=code)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
    team = get_object_or_404(Team, competition=competition, name=name)
    teams = Team.objects.filter(competition=competition)
    team_enroll_form = TeamEnrollForm()
    team_invite_limit = competition.team_size_limit - (user_team.members.count() if user_team else 0)
    team_invite_form = TeamInviteForm(team_invite_limit=team_invite_limit) if team_invite_limit != 0 else None
    update_comp_form = CompetitionCreationForm(instance=competition)

    return render(request, 'judgy/team_name.html', {
        'competition': competition,
        'user_team': user_team,
        'team': team,
        'teams': teams,
        'enroll': competition.enroll_start <= timezone.now() < competition.enroll_end,
        'update_comp_form': update_comp_form,
        'team_enroll_form': team_enroll_form,
        'team_invite_form': team_invite_form
    })
