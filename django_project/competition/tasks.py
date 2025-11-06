import math
import subprocess
from celery import shared_task
from django.conf import settings
from django.db.models import Min, Max
from django.utils.html import format_html
from pathlib import Path
from judgy.models import User
from competition.functions import run_submission
from competition.utils import notify_best_score
from competition.models import (
    Competition,
    Problem,
    Team,
    Submission,
)
from notifications.models import Notification



@shared_task
def create_images_task(competition_code):
    docker_image_script = Path(settings.BASE_DIR) / "docker_setup.sh"
    subprocess.run(f"bash {docker_image_script} {competition_code.lower()}", shell=True)

@shared_task
def process_submission(code, problem, team, user, file_paths):
    competition = Competition.objects.get(code=code)
    problem = Problem.objects.get(id=problem)
    user_team = Team.objects.get(id=team)
    user = User.objects.get(id=user)
    
    score_file, output_file, language, file_name = run_submission(code, problem, user_team, user, file_paths)
    
    with open(score_file, 'r') as f:
        score = f.read().split(' ')[0]
    with open(output_file, 'r') as f:
        file_output = f.read()

    
    if problem.show_output:
        output_url = f'/competition/{code}/{problem.name}/submission/output'
        body = format_html(
            f'You got a score of {score} in the problem "{problem.name}" for the competition "{competition.name}".<br>'
            f'Click <a href="{output_url}" target="_blank">here</a> to see the output.',
        )
    else:
        body=f'You got a score of {score} in the problem "{problem.name}" for the competition "{competition.name}".'

    Notification.objects.create(
        user=user,
        header='Your Score',
        body=body,
    )

    Notification.objects.create(user=user, header='Your Score', body=body)

    competition_submissions = Submission.objects.filter(problem=problem)
    if problem.score_preference:
        competition_best_score = competition_submissions.aggregate(Max('score'))['score__max'] or -math.inf
        if int(score) > competition_best_score:
            notify_best_score(competition, user, user_team, score, problem)
    else:
        competition_best_score = competition_submissions.aggregate(Min('score'))['score__min'] or +math.inf
        if int(score) < competition_best_score:
            notify_best_score(competition, user, user_team, score, problem)


    Submission.objects.create(
        problem=problem,
        team=user_team,
        user=user,
        language=language,
        file_name=file_name,
        output=file_output,
        score=score
    )