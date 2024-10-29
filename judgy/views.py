import logging
import json
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from pathlib import Path
from django.utils import timezone
from .forms import (
    AuthenticationForm,
    CustomUserCreationForm,
    CompetitionCreationForm,
    UploadFileForm,
    ProblemCreationForm,
    ConfirmationCodeForm
)
from .models import Competition
from .functions import start_containers
from .utils import create_comp_dir, create_problem_dir, save_problem_files

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
# from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
import random
import string

logger = logging.getLogger(__name__)


def home_view(request):
    now = timezone.now()

    past_competitions = Competition.objects.filter(end__lt=now).order_by('-end')
    ongoing_competitions = Competition.objects.filter(start__lte=now, end__gte=now).order_by('end')
    upcoming_competitions = Competition.objects.filter(start__gt=now).order_by('start')

    return render(request, 'judgy/index.html', {
        'past_competitions': past_competitions,
        'ongoing_competitions': ongoing_competitions,
        'upcoming_competitions': upcoming_competitions
    })

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("judgy:home")
    else:
        form = AuthenticationForm()
    return render(request, "judgy/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("judgy:home")

def generate_verification_code(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_verification_email(request, user, to_email):
    verification_code = generate_verification_code()  # Now generates a 6-digit numeric code
    user.verification_code = verification_code
    user.verification_code_expiration = timezone.now() + timedelta(minutes=10)  # Set expiration
    user.save()

    mail_subject = 'Welcome to Judgy!'
    message = render_to_string("../templates/judgy/activate_account_email_msg.html",
    {
        'user_name': user.first_name,
        'domain': get_current_site(request).domain,
        'protocol': 'https' if request.is_secure() else 'http',
        'verification_code': verification_code,  # Include the numeric code
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, 'Successfully created account. Please check your inbox for the verification code.')
    else:
        messages.error(request, f'Problem sending an email to {to_email}. Please verify the address.')

def register_verify_view(request):
    if request.method == "POST":
        form = ConfirmationCodeForm(request.POST)
        if form.is_valid():
            confirmation_code = ''.join([form.cleaned_data['code1'],
                                          form.cleaned_data['code2'],
                                          form.cleaned_data['code3'],
                                          form.cleaned_data['code4'],
                                          form.cleaned_data['code5'],
                                          form.cleaned_data['code6']])
            # Here you would verify the confirmation code
            expected_code = request.session.get('confirmation_code')  # Or however you're storing it

            if confirmation_code == expected_code:
                # Proceed with account verification
                messages.success(request, 'Your account has been successfully verified!')
                # return redirect('')
            else:
                messages.error(request, 'Invalid confirmation code. Please try again.')
    else:
        form = ConfirmationCodeForm()
        
    # return redirect("judgy:home")
    return render(request, "judgy/register_verify.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(request, user, user.email)
            # redirect("judgy:register_verify")
            # login(request, form.save())
            # return redirect("judgy:home")
            return redirect("judgy:register_verify")
    else:
        form = CustomUserCreationForm()
    return render(request, "judgy/register.html", {"form": form})

def set_timezone_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session["django_timezone"] = data.get("timezone")
    return redirect("judgy:home")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def competition_create_view(request):
    if request.method == "POST":
        form = CompetitionCreationForm(data=request.POST)
        if form.is_valid():
            competition = form.save()
            create_comp_dir(str(competition.code))
            return redirect("judgy:competition_code", code=competition.code)
    else:
        form = CompetitionCreationForm()
    return render(request, "judgy/competition_create.html", {"form": form})


def competition_code_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    is_superuser = request.user.is_superuser

    if request.method == "POST":
        form = ProblemCreationForm(request.POST, request.FILES)
        if form.is_valid():
            problem_name = form.cleaned_data["name"]
            problem_dir = create_problem_dir(problem_name, code)

            zip_file = request.FILES["zip"]
            input_files = request.FILES["input_files"]
            judging_program = request.FILES["judging_program"]

            save_problem_files(problem_dir, zip_file, f"{problem_name}_zip")
            save_problem_files(problem_dir, input_files, f"{problem_name}_test_files")
            save_problem_files(
                problem_dir, judging_program, f"{problem_name}_judging_program"
            )

            return redirect("judgy:competition_code", code=code)
        else:
            logger.error("Form is invalid.")
            logger.error(form.errors)

    else:
        form = ProblemCreationForm()

        context = {
            "competition": competition,
            "is_superuser": is_superuser,
            "form": form,
        }

    return render(request, "judgy/competition_code.html", context)


@login_required
def submissions(request):
    if request.method == "POST":
        logger.info("POST request received.")
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info("Form is valid.")
            current_user = request.user
            output_file, score_file = start_containers(
                request.FILES["file"], current_user
            )

            with open(output_file, "r") as f:
                user_output = f.read()

            with open(score_file, "r") as f:
                user_score = f.read()

            context = {"user_output": user_output, "user_score": user_score}

            return render(request, "judgy/submissions.html", context)

        else:
            logger.error("Form is invalid.")
            logger.error(form.errors)
            return render(request, "judgy/submissions.html", {"form": form})
    else:
        logger.info("GET request received.")
        form = UploadFileForm()
    return render(request, "judgy/submissions.html", {"form": form})
