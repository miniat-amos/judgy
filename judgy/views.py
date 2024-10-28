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
)
from .models import Competition
from .functions import start_containers
from .utils import create_comp_dir, create_problem_dir, save_problem_files

logger = logging.getLogger(__name__)


def home_view(request):
    now = timezone.now()

    past_competitions = Competition.objects.filter(end__lt=now).order_by("-end")
    ongoing_competitions = Competition.objects.filter(
        start__lte=now, end__gte=now
    ).order_by("end")
    upcoming_competitions = Competition.objects.filter(start__gt=now).order_by("start")

    return render(
        request,
        "judgy/index.html",
        {
            "past_competitions": past_competitions,
            "ongoing_competitions": ongoing_competitions,
            "upcoming_competitions": upcoming_competitions,
        },
    )


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


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect("judgy:home")
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
        form = ProblemCreationForm()
        context = {
            "competition": competition,
            "form": form,
        }

    return render(request, "judgy/competition_code.html", context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def competition_addproblems(request, code):
    competition = get_object_or_404(Competition, code=code)

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
        form = ProblemCreationForm()
        context = {
            "competition": competition,
            "form": form,
        }

    return render(request, "judgy/competition_addproblems.html", context)


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
