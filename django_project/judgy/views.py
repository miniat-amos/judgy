import json
import os
import zipfile
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.db.models import Min, Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from .decorators import verified_required
from .forms import (
    CustomUserCreationForm,
    AuthenticationForm,
    AccountVerificationForm,
    CompetitionCreationForm,
    ProblemForm,
    SubmissionForm,
    TeamEnrollForm,
    TeamInviteForm
)
from .functions import (
    create_images,
    start_containers
)
from .models import (
  User,
  Competition,
  Problem,
  Team,
  Submission,
  Notification,
  TeamJoinNotification,
  TeamInviteNotification
)
from .utils import (
    create_comp_dir,
    create_problem,
    get_dist_dir
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
        form = AccountVerificationForm(data=request.POST)
        form.user = request.user
        if form.is_valid():
            request.user.is_verified = True
            request.user.save()
            return redirect('judgy:home')
    else:
        form = AccountVerificationForm()
    return render(request, 'judgy/verify.html', {'form': form})

@verified_required
def notifications_view(request):
    return JsonResponse(list(Notification.objects.filter(user=request.user).values()), safe=False)

@verified_required
def notification_clear_view(request, id):
    notification = get_object_or_404(Notification, id=id, user=request.user)
    notification.delete()
    return JsonResponse({})

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
    problems = Problem.objects.filter(competition=competition)
    
    
    # Fetch best scores using Python logic for each problem and team
    for problem in problems:        
        submissions = Submission.objects.filter(problem=problem, user=request.user)
        if problem.score_preference:  # Higher score is better
            best_score = submissions.aggregate(Max('score'))['score__max']
        else:  # Lower score is better
            best_score = submissions.aggregate(Min('score'))['score__min']
        problem.best_score = best_score or 0

    if request.method == 'GET':
        problem_form = ProblemForm()
        team_enroll_form = TeamEnrollForm()
        team_invite_limit = competition.team_size_limit - (user_team.members.count() if user_team else 0)
        team_invite_form = TeamInviteForm(team_invite_limit=team_invite_limit) if team_invite_limit != 0 else None
        return render(request, 'judgy/competition_code.html', {
            'competition': competition,
            'user_team': user_team,
            'teams': teams,
            'problem_form': problem_form,
            'team_enroll_form': team_enroll_form,
            'team_invite_form': team_invite_form,
            'problems': problems,
        })

    if request.method == 'DELETE':
        if request.user.is_authenticated and request.user.is_superuser:
            competition.delete()
            return JsonResponse({})

@user_passes_test(lambda u: u.is_superuser)
def problems_update_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == 'POST':
        problem_form = ProblemForm(request.POST, request.FILES)
        if (problem_form.is_valid()):
            problem = problem_form.save(commit=False)
            problem.number = 1
            problem.competition = competition
            problem.save()

            description = request.FILES.get('description')
            judge_py = request.FILES.get('judge_py')
            other_files = request.FILES.getlist('other_files')

            dist = [
                key[len('distribute['):-1]
                for key, val in request.POST.items()
                if key.startswith('distribute[')
            ]

            create_problem(code, problem.name, description, judge_py, other_files, dist)
            
            
            return redirect('judgy:competition_code', code=competition.code)

@verified_required
def team_enroll_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == 'POST':
        if competition.enroll_start <= timezone.now() < competition.enroll_end:
            form = TeamEnrollForm(data=request.POST)
            if form.is_valid():
                name = form.cleaned_data.get('name')
                team, created = Team.objects.get_or_create(
                    competition=competition,
                    name=name
                )
                if created:
                    team.members.add(request.user)
                else:
                    for member in team.members.all():
                        user = member
                        body = f'Hi {member.first_name}, {request.user} wants to join your team "{team.name}" for the competition "{competition.name}".'
                        TeamJoinNotification.objects.create(user=user, body=body, request_user=request.user, team=team)
                return redirect('judgy:team_name', code=team.competition.code, name=team.name)

@verified_required
def team_join_accept_view(request, id):
    notification = get_object_or_404(TeamJoinNotification, id=id, user=request.user)
    team = notification.team
    competition = team.competition

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        for member in team.members.all():
            if member != request.user:
                Notification.objects.create(
                    user=member,
                    header='Update',
                    body=f'{request.user} has accepted the request of {notification.request_user} to join the team.'
                )
        Notification.objects.create(
            user=notification.request_user,
            header='Update',
            body=f'"{team.name}" has accepted your request to join the team.'
        )
        team.members.add(notification.request_user)
        TeamJoinNotification.objects.filter(request_user=notification.request_user, team=team).delete()
        return JsonResponse({})

@verified_required
def team_join_decline_view(request, id):
    notification = get_object_or_404(TeamJoinNotification, id=id, user=request.user)
    team = notification.team
    competition = team.competition

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        for member in team.members.all():
            if member != request.user:
                Notification.objects.create(
                    user=member,
                    header='Update',
                    body=f'{request.user} has declined the request of {notification.request_user} to join the team.'
                )
        Notification.objects.create(
            user=notification.request_user,
            header='Update',
            body=f'"{team.name}" has declined your request to join the team.'
        )
        TeamJoinNotification.objects.filter(request_user=notification.request_user, team=team).delete()
        return JsonResponse({})

@verified_required
def team_leave_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        team = Team.objects.filter(competition=competition, members=request.user).first()
        if team:
            team.members.remove(request.user)
            if team.members.count():
                for member in team.members.all():
                    Notification.objects.create(
                        user=member,
                        header='Update',
                        body=f'{request.user} left the team.'
                    )
            else:
                team.delete()
            return JsonResponse({})

@verified_required
def team_invite_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == 'POST':
        if competition.enroll_start <= timezone.now() < competition.enroll_end:
            team = Team.objects.filter(competition=competition, members=request.user).first()
            team_invite_limit = competition.team_size_limit - (team.members.count() if team else 0)
            form = TeamInviteForm(data=request.POST, team_invite_limit=team_invite_limit)
            if form.is_valid():
                for field in form.fields:
                    email = form.cleaned_data[field]
                    if email:
                        user = User.objects.get(email=email)
                        body = f'Hi {user.first_name}, {request.user} has invited you to join the team "{team.name}" for the competition "{competition.name}".'
                        TeamInviteNotification.objects.create(user=user, body=body, team=team)
                return redirect('judgy:team_name', code=team.competition.code, name=team.name)

@verified_required
def team_invite_accept_view(request, id):
    notification = get_object_or_404(TeamInviteNotification, id=id, user=request.user)
    team = notification.team
    competition = team.competition

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        for member in team.members.all():
            Notification.objects.create(
                user=member,
                header='Update',
                body=f'{request.user} has accepted the invitation to join the team.'
            )
        team.members.add(request.user)
        notification.delete()
        return JsonResponse({})

@verified_required
def team_invite_decline_view(request, id):
    notification = get_object_or_404(TeamInviteNotification, id=id, user=request.user)
    team = notification.team
    competition = team.competition

    if competition.enroll_start <= timezone.now() < competition.enroll_end:
        for member in team.members.all():
            Notification.objects.create(
                user=member,
                header='Update',
                body=f'{request.user} has declined the invitation to join the team.'
            )
        notification.delete()
        return JsonResponse({})

def team_name_view(request, code, name):
    competition = get_object_or_404(Competition, code=code)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
    team = get_object_or_404(Team, competition=competition, name=name)
    teams = Team.objects.filter(competition=competition)
    team_enroll_form = TeamEnrollForm()
    team_invite_limit = competition.team_size_limit - (user_team.members.count() if user_team else 0)
    team_invite_form = TeamInviteForm(team_invite_limit=team_invite_limit) if team_invite_limit != 0 else None
    return render(request, 'judgy/team_name.html', {
        'competition': competition,
        'user_team': user_team,
        'team': team,
        'teams': teams,
        'team_enroll_form': team_enroll_form,
        'team_invite_form': team_invite_form
    })

def competitions_view(request):
    return JsonResponse(list(Competition.objects.all().values()), safe=False)

@verified_required
def submit_view(request, code, problem_name):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            current_user = request.user
            competition = Competition.objects.get(code=code)
            user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
            problem = Problem.objects.get(name=problem_name, competition=competition)
            # submitted_file = request.FILES['file']
            submitted_files = request.FILES.getlist('file')
            output_file, score_file = start_containers(submitted_files, current_user, user_team, code, problem_name)

            with open(score_file, 'r') as f:
                user_score = f.read()

            user_score = user_score.split(' ')[0]

            Submission.objects.create(score=user_score, problem=problem, team=user_team, user=current_user)

            Notification.objects.create(
                user=request.user,
                header='Update',
                body=f'score is {user_score}'
            )

            return redirect('judgy:competition_code', code=code)

def download_view(request, code, problem_name):
    dist_dir = get_dist_dir(code, problem_name)

    problem_zip = f'/tmp/{problem_name}.zip'

     # Create a zip file
    with zipfile.ZipFile(problem_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, dist_dir))

     # Read the zip file and return it in an HTTP response
    with open(problem_zip, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/zip')
        # Set the Content-Disposition header to prompt the user to download the file
        response['Content-Disposition'] = f'attachment; filename="{problem_name}.zip"'

    os.remove(problem_zip)

    return response
