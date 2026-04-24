import subprocess
from celery import shared_task
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from pathlib import Path
from judgy.models import User
from competition.docker_functions import create_images, run_submission
from competition.utils import notify_admin_submission, check_competition_best
from competition.models import (
    Competition,
    Problem,
    Team,
    Submission,
)
from notifications.models import Notification

@shared_task
def celery_build_judgy_images():
    create_images.build_judgy_images()


@shared_task
def celery_process_submission(code, problem, team, user, submission, user_directories, user_submission):
    competition = Competition.objects.get(code=code)
    problem = Problem.objects.get(id=problem)
    user_team = Team.objects.get(id=team)
    user = User.objects.get(id=user)
    submission = Submission.objects.get(id=submission)
    
    if not problem.subjective:
    
        score_file, output_file, language, file_name = run_submission.run_submission(code, user, problem, user_submission, user_directories)

        with open(score_file, 'r') as f:
            submission_score = f.read()
        with open(output_file, 'r') as f:
            submission_output = f.read()
            
        split_score = submission_score.split(' ')[0]
            

        if split_score == "FAILED:":
            error = submission_score.split('FAILED: ')[1]
            submission_score = None
            
            output_url = reverse('competition:output', kwargs={'code': code, 'problem_name': problem.name})
            body = format_html(
                f'Your program failed with the error: "{error}" in the problem "{problem.name}" for the competition "{competition.name}".<br>'
                f'Click <a href="{output_url}" target="_blank">here</a> to see more details.',
            )
                
            Notification.objects.create(
                user=user,
                header='Your Error',
                body=body,
            )

        else:
            try:
                score = int(split_score)
            except ValueError:
                print("error")
            else:
                submission.score = score
                if problem.show_output:
                    output_url = reverse('competition:output', kwargs={'code': code, 'problem_name': problem.name})
                    body = format_html(
                        f'You got a score of {score} in the problem "{problem.name}" for the competition "{competition.name}".<br>'
                        f'Click <a href="{output_url}" target="_blank">here</a> to see the output.',
                    )
                else:
                    body = f'You got a score of {score} in the problem "{problem.name}" for the competition "{competition.name}".'

                Notification.objects.create(
                    user=user,
                    header='Your Score',
                    body=body,
                )

                check_competition_best(competition, problem, score, user, user_team)
        
        submission.language = language
        submission.file_name = file_name
        submission.output = submission_output
        
        submission.save(update_fields=['language', 'file_name', 'output', 'score'])
        

    else:
    
        Notification.objects.create(
            user=user,
            header='Your Submission',
            body='The file you uploaded has been successfully submitted.',
        )
        
        notify_admin_submission(competition, user, user_team, problem)
        


   