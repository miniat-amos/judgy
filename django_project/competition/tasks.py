import subprocess
from celery import shared_task
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from pathlib import Path
from judgy.models import User
from competition.functions import run_submission, get_language
from competition.utils import notify_admin_submission, create_user_dir, store_submissions, check_competition_best
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
    
    if not problem.subjective:
        
        score_file, output_file, language, file_name = run_submission(code, problem, user_team, user, file_paths)

        with open(score_file, 'r') as f:
            score = f.read().split(' ')[0]
        with open(output_file, 'r') as f:
            file_output = f.read()
     
        if problem.show_output:
            output_url = reverse('competition:output', kwargs={'code': code, 'problem_name': problem.name})
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

        check_competition_best(competition, problem, score, user, user_team)
        
        Submission.objects.create(
            problem=problem,
            team=user_team,
            user=user,
            language=language,
            file_name=file_name,
            output=file_output,
            score=score
        )

    else:
        _, language = get_language(file_paths)
        submission = Submission.objects.create(
            problem=problem,
            team=user_team,
            user=user,
            language=language,
            file_name="",
            output=None,
            score=0
        )
        
        submission_dir = create_user_dir(code, user, problem.name, user_team, submission, subjective=problem.subjective)

        submitted_files = store_submissions(file_paths, submission_dir)
        
        Notification.objects.create(
            user=user,
            header='Your Submission',
            body=f'Your file you uploaded has been successfully submitted.',
        )
        
        notify_admin_submission(competition, user, user_team, problem)

      
  