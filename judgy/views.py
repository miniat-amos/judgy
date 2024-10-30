import json
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import (
    AuthenticationForm,
    CompetitionCreationForm,
    CustomUserCreationForm,
    ProblemCreationForm,
    ConfirmationCodeForm,
    UploadFileForm
)
from .models import Competition
from .functions import start_containers, create_images
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

    past_competitions = Competition.objects.filter(end__lt=now).order_by("-end")
    ongoing_competitions = Competition.objects.filter(start__lte=now, end__gte=now).order_by("end")
    upcoming_competitions = Competition.objects.filter(start__gt=now).order_by("start")

    return render(
        request,
        "judgy/index.html",
        {
            "past_competitions": past_competitions,
            "ongoing_competitions": ongoing_competitions,
            "upcoming_competitions": upcoming_competitions
        }
    )

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("judgy:home")
    else:
        form = AuthenticationForm()
    return render(request, "judgy/login.html", { "form": form })

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
    return render(request, "judgy/competition_create.html", { "form": form })

def competition_code_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == "GET":
        form = ProblemCreationForm()
        return render(request, "judgy/competition_code.html", {
            "competition": competition,
            "form": form
        })

    if request.method == "POST":
        form = ProblemCreationForm(request.POST, request.FILES)
        if form.is_valid():
            row_numbers = request.POST.getlist("row_number")
            problem_names = request.POST.getlist("name")
            zip_files = request.FILES.getlist("zip")
            input_files = request.FILES.getlist("input_files")
            judging_programs = request.FILES.getlist("judging_program")

            for i, row in enumerate(row_numbers):
                name = problem_names[i]
                zip_file = zip_files[i]
                input_file = input_files[i]
                judging_program = judging_programs[i]
                problem_dir = create_problem_dir(name, code)

                directories = [
                    f"{name}_zip",
                    f"{name}_input_file",
                    f"{name}_judging_program"
                ]

                file_names = [
                    f"{name}.zip",
                    f"{name}-{input_file.name}",
                    f"{name}-judge.py"
                ]

                files = [zip_file, input_file, judging_program]

                save_problem_files(problem_dir, directories, file_names, files)
                create_images(code)

            return redirect("judgy:competition_code", code=code)
        return render(request, "judgy/competition_code.html", {
            "competition": competition,
            "form": form
        })
    
    if request.method == "PUT":
        pass

    if request.method == "DELETE":
        if request.user.is_authenticated and request.user.is_superuser:
            competition.delete()
            return JsonResponse({})

@login_required
def submissions(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            current_user = request.user
            submitted_file = request.FILES["file"]
            output_file, score_file = start_containers(submitted_file, current_user)

            with open(output_file, "r") as f:
                user_output = f.read()

            with open(score_file, "r") as f:
                user_score = f.read()

            return render(request, "judgy/submissions.html", {
                "user_output": user_output,
                "user_score": user_score
            })
        else:
            return render(request, "judgy/submissions.html", {"form": form})
    else:
        form = UploadFileForm()
    return render(request, "judgy/submissions.html", { "form": form })
