from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from judgy.models import Competition, Problem, Team, Submission


def competition_scores(request, code):
    competition = get_object_or_404(Competition, code=code)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
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
        

        competition_scores = (
            {
                "competition_best_score": problem.competition_best_scores,
                "test_best_score": problem.team_best_score,
                "user_best_score": problem.user_best_score
            }
        )
        
    return JsonResponse(competition_scores, safe=False)