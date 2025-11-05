from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from competition.forms import (
    CompetitionCreationForm,
    ProblemForm,
    SubmissionForm,
    TeamEnrollForm,
    TeamInviteForm
)
from competition.models import Competition, Problem, Team, Submission

def competition_code_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
    teams = Team.objects.filter(competition=competition)
    problems = Problem.objects.filter(competition=competition).order_by('number')
    
    for problem in problems:
        competition_submissions = Submission.objects.filter(problem=problem)
        team_submissions = Submission.objects.filter(problem=problem, team=user_team)
        user_submissions = Submission.objects.filter(problem=problem, team=user_team, user=request.user if request.user.is_authenticated else None)
        if problem.score_preference: # Higher Score is Better
            problem.competition_best_score = str(competition_submissions.aggregate(Max('score'))['score__max']) if competition_submissions else ""
            problem.team_best_score = str(team_submissions.aggregate(Max('score'))['score__max']) if team_submissions else ""
            problem.user_best_score = str(user_submissions.aggregate(Max('score'))['score__max']) if user_submissions else ""
        else: # Lower Score is Better
            problem.competition_best_score = str(competition_submissions.aggregate(Max('score'))['score__min']) if competition_submissions else ""
            problem.team_best_score = str(team_submissions.aggregate(Max('score'))['score__min']) if team_submissions else ""
            problem.user_best_score = str(user_submissions.aggregate(Max('score'))['score__min']) if user_submissions else ""

    if request.method == 'GET':
        problem_form = ProblemForm()
        update_comp_form = CompetitionCreationForm(instance=competition)
        submission_form = SubmissionForm()
        team_enroll_form = TeamEnrollForm()
        team_invite_limit = competition.team_size_limit - (user_team.members.count() if user_team else 0)
        team_invite_form = TeamInviteForm(team_invite_limit=team_invite_limit) if team_invite_limit != 0 else None
        return render(request, 'judgy/competition_code.html', {
            'competition': competition,
            'user_team': user_team,
            'teams': teams,
            'problem_form': problem_form,
            'update_comp_form': update_comp_form,
            'submission_form': submission_form,
            'team_enroll_form': team_enroll_form,
            'team_invite_form': team_invite_form,
            'problems': problems,
            'download': competition.start <= timezone.now(),
            'upload': competition.start <= timezone.now() < competition.end and user_team,
            'enroll': competition.enroll_start <= timezone.now() < competition.enroll_end,
            'is_competition_over': competition.end <= timezone.now()
        })

    if request.method == 'DELETE':
        if request.user.is_superuser:
            competition.delete()
            return JsonResponse({})
        else:
            print('User is not authenticated and is not a super user. Competition not deleted.')
