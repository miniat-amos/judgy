from django.db.models.signals import post_save
from django.db.models import Max, Min
from django.dispatch import receiver
from competition.models import Submission
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import logging

logger = logging.getLogger(__name__)


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

    logger.info("Computed bests:", competition_best, team_best, user_best)
    
    data = [{
        "problem": problem.name,
        "competition_best": competition_best,
        "team_best": team_best,
        "user_best": user_best,
    }]

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"competition_{problem.competition.code}",
        {
            "type": "score_update",
            "data": data
        }
    )


