from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from competition.models import Competition, Problem, Team

def get_competition_problems(request, code):
    competition = get_object_or_404(Competition, code=code)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
    teams = Team.objects.filter(competition=competition)
    problems = Problem.objects.filter(competition=competition).order_by('number')
    
    problems = []
    for problem in problems:
        problems.append({
            'number': problem.number,
            'name': problem.name,
            'score_preference': problem.score_preference,
            'team_best_score': getattr(problem.get_team_score(user_team), 'score', None) if user_team else None,
            'user_best_score': getattr(problem.get_user_score(request.user), 'score', None),
            'competition_best_score': getattr(problem.get_competition_best_score(), 'score', None),
            'can_download': user_team or request.user.is_superuser or competition.is_over,
            'can_upload': user_team is not None and not competition.is_over,
        })
    
    # for problem in problems:
    #     competition_submissions = Submission.objects.filter(problem=problem)
    #     team_submissions = Submission.objects.filter(problem=problem, team=user_team)
    #     user_submissions = Submission.objects.filter(problem=problem, team=user_team, user=request.user if request.user.is_authenticated else None)
    #     if problem.score_preference: # Higher Score is Better
    #         problem.competition_best_score = str(competition_submissions.aggregate(Max('score'))['score__max']) if competition_submissions else ""
    #         problem.team_best_score = str(team_submissions.aggregate(Max('score'))['score__max']) if team_submissions else ""
    #         problem.user_best_score = str(user_submissions.aggregate(Max('score'))['score__max']) if user_submissions else ""
    #     else: # Lower Score is Better
    #         problem.competition_best_score = str(competition_submissions.aggregate(Max('score'))['score__min']) if competition_submissions else ""
    #         problem.team_best_score = str(team_submissions.aggregate(Max('score'))['score__min']) if team_submissions else ""
    #         problem.user_best_score = str(user_submissions.aggregate(Max('score'))['score__min']) if user_submissions else ""

    if request.method == 'GET':

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
