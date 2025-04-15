import subprocess
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.conf import settings

from pathlib import Path

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