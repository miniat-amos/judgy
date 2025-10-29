from django.db.models import Min, Max
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from ..models import Competition, Team, Problem, Submission


def get_member_scores(request, code, name):
    competition = get_object_or_404(Competition, code=code)
    team = get_object_or_404(Team, competition=competition, name=name)
    members = team.members.all().values('id', 'email', 'first_name', 'last_name')
    problems = Problem.objects.filter(competition=competition).order_by('number')
        
    member_scores = {
        'team': team.name,
        'members': {}
    }
    
    for member in members:
        email = member['email']
        member_scores['members'][email] = {
            'first_name': member['first_name'],
            'last_name': member['last_name'],
            'scores': {}
        }

        for problem in problems:
            user_submissions = Submission.objects.filter(problem=problem, team=team, user=member['id'])
            latest_submission = Submission.objects.filter(problem=problem, team=team, user=member['id']).order_by('-pk').first()
            if problem.score_preference: # Higher Score is Better
                user_best_score = user_submissions.order_by('-score').first()
            else: # Lower Score is Better
                user_best_score = user_submissions.order_by('score').first()
            
            print(user_best_score.id)        
            if user_best_score:
                member_scores['members'][email]['scores'][problem.name] = {
                    "submission_id": latest_submission.id,
                    "problem_number": problem.number,
                    'score_preference': problem.score_preference,
                    "member_score": str(user_best_score.score) if user_best_score is not None else "",
                    "subjective": problem.subjective
                }

    return JsonResponse(member_scores, safe=False)