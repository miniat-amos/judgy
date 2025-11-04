import math
import subprocess
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Min, Max
from django.utils.html import format_html
from pathlib import Path
from judgy.models import (
    Competition,
    Problem,
    Team,
    Submission,
    User
)
from judgy.functions import run_submission
from notifications.models import Notification

@shared_task
def send_6dc_email_task(user_id, user_email):

    User = get_user_model()
    user = User.objects.get(id=user_id)

    send_mail(
                'Welcome to judgy!',
                render_to_string('judgy/emails/account_verification.html', { 'user': user }),
                settings.EMAIL_HOST_USER,
                [user_email],
                html_message=render_to_string('judgy/emails/account_verification.html', { 'user': user })
            )
    
@shared_task
def create_images_task(competition_code):
    docker_image_script = Path(settings.BASE_DIR) / "docker_setup.sh"
    subprocess.run(f"bash {docker_image_script} {competition_code.lower()}", shell=True)

@shared_task
def process_submission(code, competition, problem_id, problem_name, team_id, user_id, file_paths):
    competition = Competition.objects.get(code=competition)
    problem = Problem.objects.get(id=problem_id)
    user_team = Team.objects.get(id=team_id)
    user = User.objects.get(id=user_id)
    
    score_file, output_file, language, file_name = run_submission(code, problem, user_team, user, file_paths)
    
    with open(score_file, 'r') as f:
        score = f.read().split(' ')[0]
    with open(output_file, 'r') as f:
        file_output = f.read()

    Submission.objects.create(
        problem=problem,
        team=user_team,
        user=user,
        language=language,
        file_name=file_name,
        output=file_output,
        score=score
    )
    
    if problem.show_output:
        output_url = f'/competition/{code}/{problem_name}/submission/output'
        body = format_html(
            f'You got a score of {score} in the problem "{problem_name}" for the competition "{competition.name}".<br>'
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
            notify_best_score(user, user_team, score, problem)
    else:
        competition_best_score = competition_submissions.aggregate(Min('score'))['score__min'] or +math.inf
        if int(score) < competition_best_score:
            notify_best_score(user, user_team, score, problem)

def notify_best_score(user, team, score, problem):
    competition = problem.competition
    superusers = User.objects.filter(is_superuser=True)
    participants = User.objects.filter(teams__competition=competition)
    header = 'New Best Score'
    body = f'{user.first_name} from team "{team}" has achieved a new best score of {score} in "{problem.name}" for competition "{competition.name}"!'
    for u in superusers.union(participants):
        Notification.objects.create(user=u, header=header, body=body)