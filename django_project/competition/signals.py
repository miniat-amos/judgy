from django.db.models.signals import post_save
from django.db.models import Max, Min
from django.dispatch import receiver
from competition.models import Submission
from competition.utils import (
    send_competition_best, 
    send_team_best,
    send_user_best
)

@receiver(post_save, sender=Submission)
def check_best_score(sender, instance, created, **kwargs):
    if not created:
        return
    
    problem = instance.problem
    team = instance.team
    user = instance.user
    
    competition_submissions = Submission.objects.filter(problem=problem)
    team_submissions = competition_submissions.filter(team=team)
    user_submissions = competition_submissions.filter(user=user)

    if problem.score_preference:  # Higher Score is Better
        agg_func = Max
        key_name = 'score__max'
    else:  # Lower Score is Better
        agg_func = Min
        key_name = 'score__min'

    competition_best = competition_submissions.aggregate(agg_func('score'))[key_name]
    team_best = team_submissions.aggregate(agg_func('score'))[key_name]
    user_best = user_submissions.aggregate(agg_func('score'))[key_name]
    
    
    send_competition_best(problem, competition_best)
    send_team_best(problem, team, team_best)
    send_user_best(problem, user, user_best)
    




