import math
from datetime import timedelta
from django.db.models import Min, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import Competition, Problem, Team, Submission

def rankings_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    problems = Problem.objects.filter(competition=competition)
    teams = Team.objects.filter(competition=competition)

    rankings = []
    score_map = {problem.name: [] for problem in problems}
    time_list = []

    for team in teams:
        
        team_data = {
            'team_name': team.name,
            'members': [member.first_name for member in team.members.all()],
            'total_attempt': 0,
            'total_time': timedelta(0)
        }
        
        for problem in problems:
            # Get submissions for the current problem and team
            submissions = Submission.objects.filter(problem=problem, team=team)

                        
            # Determine the best submission based on score preference
            if problem.score_preference: # Higher Score is better
                best_submission = submissions.order_by('-score', 'time').first()
            else: # Lower Score is better
                best_submission = submissions.order_by('score', 'time').first()
            
            if best_submission:
                best_score = best_submission.score
                best_time = best_submission.time - competition.start
                team_data['total_attempt'] += 1
            else:
                # Assign default values for no submissions
                best_score = -math.inf if problem.score_preference else +math.inf
                best_time = competition.end - competition.start
            
            team_data[problem.name] = {'best_score': best_score, 'best_time': best_time}
            score_map[problem.name].append(best_score)
            team_data['total_time'] += best_time

        rankings.append(team_data)
        time_list.append(team_data['total_time'])

    # Assign ranks for each problem based on best score
    for problem in problems:
        scores = score_map[problem.name]
        ranked_scores = sorted(set(scores), reverse=problem.score_preference)
        
        for team in rankings:
            team[problem.name]['score_rank'] = ranked_scores.index(team[problem.name]['best_score']) + 1
    
    for team in rankings:
        team['total_score'] = sum(
            team[problem.name]['score_rank'] for problem in problems
        )

    # Clean up infinite scores
    for team in rankings:
        for problem in problems:
            score = team[problem.name]['best_score']
            team[problem.name]['best_score'] = score if math.isfinite(score) else None

    # Assign ranks based on total attempt
    ranked_attempts = sorted(set(team['total_attempt'] for team in rankings), reverse=True)
    
    for team in rankings:
        team['attempt_rank'] = ranked_attempts.index(team['total_attempt']) + 1

    # Assign ranks based on total score
    ranked_scores = sorted(set(team['total_score'] for team in rankings))
    
    for team in rankings:
        team['score_rank'] = ranked_scores.index(team['total_score']) + 1

    # Assign ranks based on total time
    ranked_times = sorted(set(time_list))

    for team in rankings:
        team['time_rank'] = ranked_times.index(team['total_time']) + 1

    # Finalize team rankings
    rankings.sort(key=lambda team: (
        team['attempt_rank'],
        team['score_rank'],
        team['time_rank'],
        team['team_name']
    ))

    rank = 1
    for i, team in enumerate(rankings):
        if i > 0:
            prev_team = rankings[i - 1]
            is_tied = (
                team['attempt_rank'] == prev_team['attempt_rank'] and
                team['score_rank'] == prev_team['score_rank'] and
                team['time_rank'] == prev_team['time_rank']
            )
            if not is_tied:
                rank = i + 1
        team['rank'] = rank

    return JsonResponse([{
        'rank': team['rank'],
        'team_name': team['team_name'],
        'members': team['members'],
        'attempt_rank': team['attempt_rank'],
        'score_rank': team['score_rank'],
        'time_rank': team['time_rank'],
        'total_attempt': team['total_attempt'],
        'total_score': team['total_score'],
        'total_time': team['total_time'],
        **{f'{problem.name}': {
            'score_rank': team[problem.name]['score_rank'],
            'best_score': team[problem.name]['best_score'],
            'best_time': team[problem.name]['best_time']
        } for problem in problems}
    } for team in rankings], safe=False)
