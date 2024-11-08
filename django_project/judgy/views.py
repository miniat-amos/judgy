import json
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from .decorators import verified_required
from .forms import (
    CustomUserCreationForm,
    AuthenticationForm,
    AccountVerificationForm,
    CompetitionCreationForm,
    TeamCreationForm,
    ProblemCreationForm,
    UploadFileForm
)
from .functions import (
    create_images,
    start_containers
)
from .models import Competition, Team
from .utils import (
    create_comp_dir,
    create_problem_dir,
    save_problem_files
)

def home_view(request):
    now = timezone.now()

    past_competitions = Competition.objects.filter(end__lte=now).order_by('-end')
    ongoing_competitions = Competition.objects.filter(
        start__lte=now, end__gt=now
    ).order_by('end')
    upcoming_competitions = Competition.objects.filter(start__gt=now).order_by('start')

    return render(
        request,
        'judgy/index.html',
        {
            'past_competitions': past_competitions,
            'ongoing_competitions': ongoing_competitions,
            'upcoming_competitions': upcoming_competitions,
        },
    )

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('judgy:home')
    else:
        form = AuthenticationForm()
    return render(request, 'judgy/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('judgy:home')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_mail(
                'Welcome to judgy!',
                render_to_string('judgy/emails/account_verification.html', { 'user': user }),
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=render_to_string('judgy/emails/account_verification.html', { 'user': user })
            )
            return redirect('judgy:verify')
    else:
        form = CustomUserCreationForm()
    return render(request, 'judgy/register.html', {'form': form})

def verify_view(request):
    if request.method == 'POST':
        form = AccountVerificationForm(request.POST)
        form.user = request.user
        if form.is_valid():
            request.user.is_verified = True
            request.user.save()
            return redirect('judgy:home')
    else:
        form = AccountVerificationForm()
    return render(request, 'judgy/verify.html', {'form': form})

def set_timezone_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['django_timezone'] = data.get('timezone')
    return redirect('judgy:home')

@user_passes_test(lambda u: u.is_superuser)
def competition_create_view(request):
    if request.method == 'POST':
        form = CompetitionCreationForm(data=request.POST)
        if form.is_valid():
            competition = form.save()
            create_comp_dir(str(competition.code))
            return redirect('judgy:competition_code', code=competition.code)
    else:
        form = CompetitionCreationForm()
    return render(request, 'judgy/competition_create.html', {'form': form})

def competition_code_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
    teams = Team.objects.filter(competition=competition)

    if request.method == 'GET':
        team_creation_form = TeamCreationForm()
        problem_creation_form = ProblemCreationForm()
        return render(request, 'judgy/competition_code.html', {
            'competition': competition,
            'user_team': user_team,
            'teams': teams,
            'team_creation_form': team_creation_form,
            'problem_creation_form': problem_creation_form
        })

    if request.method == 'POST':
        problem_creation_form = ProblemCreationForm(request.POST, request.FILES)
        if problem_creation_form.is_valid():
            row_numbers = request.POST.getlist('row_number')
            problem_names = request.POST.getlist('name')
            zip_files = request.FILES.getlist('zip')
            input_files = request.FILES.getlist('input_files')
            judging_programs = request.FILES.getlist('judging_program')

            for i, row in enumerate(row_numbers):
                name = problem_names[i]
                zip_file = zip_files[i]
                input_file = input_files[i]
                judging_program = judging_programs[i]
                problem_dir = create_problem_dir(name, code)

                directories = [
                    f'{name}_zip',
                    f'{name}_input_file',
                    f'{name}_judging_program'
                ]

                file_names = [
                    f'{name}.zip',
                    f'{name}-{input_file.name}',
                    f'{name}-judge.py'
                ]

                files = [zip_file, input_file, judging_program]

                save_problem_files(problem_dir, directories, file_names, files)
                create_images(code)

            return redirect('judgy:competition_code', code=code)
        return render(request, 'judgy/competition_code.html', {
            'competition': competition,
            'problem_creation_form': problem_creation_form
        })
    
    if request.method == 'PUT':
        pass

    if request.method == 'DELETE':
        if request.user.is_authenticated and request.user.is_superuser:
            competition.delete()
            return JsonResponse({})

@verified_required
def team_create_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == 'POST':
        if competition.enroll_start <= timezone.now() < competition.enroll_end:
            form = TeamCreationForm(data=request.POST)
            if form.is_valid():
                team = form.save(commit=False)
                team.competition = competition
                team.save()
                team.members.add(request.user)
                return redirect('judgy:team_name', code=team.competition.code, name=team.name)
        
def team_name_view(request, code, name):
    competition = get_object_or_404(Competition, code=code)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
    team = get_object_or_404(Team, competition=competition, name=name)
    return render(request, 'judgy/team_name.html', {
        'competition': competition,
        'user_team': user_team,
        'team': team
    })

def competitions_view(request):
    return JsonResponse(list(Competition.objects.all().values()), safe=False)

@verified_required
def submissions(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            current_user = request.user
            submitted_file = request.FILES['file']
            output_file, score_file = start_containers(submitted_file, current_user)

            with open(output_file, 'r') as f:
                user_output = f.read()

            with open(score_file, 'r') as f:
                user_score = f.read()

            return render(
                request,
                'judgy/submissions.html',
                {'user_output': user_output, 'user_score': user_score},
            )
        else:
            return render(request, 'judgy/submissions.html', {'form': form})
    else:
        form = UploadFileForm()
    return render(request, 'judgy/submissions.html', {'form': form})
