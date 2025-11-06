from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from competition.models import Competition, Team, Problem, Submission


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
            'submissions': {}
        }

        for problem in problems:
            user_submissions = Submission.objects.filter(problem=problem, team=team, user=member['id']).order_by('-time')
        
            if user_submissions:
                    total_submissions = len(user_submissions)
                    member_scores['members'][email]['submissions'] = [
                    {
                        "submission_id": submission.id,
                        "submission_number": total_submissions - i,
                        "problem_number": problem.number,
                        "problem_name": problem.name,
                        "score_preference": problem.score_preference,
                        "score": submission.score,
                        "subjective": problem.subjective,
                    }
                    for i, submission in enumerate(user_submissions)
            
                ]


    return JsonResponse(member_scores, safe=False)