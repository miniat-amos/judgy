import json
import math
import os
import zipfile
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.db.models import Min, Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
    run_submission
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
    get_dist_dir,
    team_add_user,
)
from .tasks import (
    send_6dc_email_task,
    create_images_task,
)

from .serializers import (
    CompSerializer,
)

def home_view(request):
    now = timezone.now()

    past_competitions = Competition.objects.filter(end__lte=now).order_by('-end')
    ongoing_competitions = Competition.objects.filter(
        start__lte=now, end__gt=now
    ).order_by('end')
    upcoming_competitions = Competition.objects.filter(start__gt=now).order_by('start')
    
    update_comp_form = CompetitionCreationForm()


    return render(
        request,
        'judgy/index.html',
        {
            'past_competitions': past_competitions,
            'ongoing_competitions': ongoing_competitions,
            'upcoming_competitions': upcoming_competitions,
            'update_comp_form': update_comp_form,

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
            send_6dc_email_task.delay(user.id, user.email)
            return redirect('judgy:verify')
        else:
            print('Any field in the registration form was not filled out right.')
            print('form.errors:\n', form.errors)
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
            print('6-digit code provided is incorrect')
            print('form.errors:\n', form.errors)
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
            print('Any field filled out is invalid.')
            print('form.errors:\n', form.errors)
    else:
        form = CompetitionCreationForm()
    return render(request, 'judgy/competition_create.html', {'form': form})

def competition_code_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
    teams = Team.objects.filter(competition=competition)
    problems = Problem.objects.filter(competition=competition).order_by('number')
    
    for problem in problems:
        competition_submissions = Submission.objects.filter(problem=problem)
        team_submissions = Submission.objects.filter(problem=problem, team=user_team)
        user_submissions = Submission.objects.filter(problem=problem, team=user_team, user=request.user if request.user.is_authenticated else None)
        if problem.score_preference: # Higher Score is Better
            problem.competition_best_score = competition_submissions.aggregate(Max('score'))['score__max']
            problem.team_best_score = team_submissions.aggregate(Max('score'))['score__max']
            problem.user_best_score = user_submissions.aggregate(Max('score'))['score__max'] 
        else: # Lower Score is Better
            problem.competition_best_score = competition_submissions.aggregate(Min('score'))['score__min']
            problem.team_best_score = team_submissions.aggregate(Min('score'))['score__min']
            problem.user_best_score = user_submissions.aggregate(Min('score'))['score__min']

    if request.method == 'GET':
        problem_form = ProblemForm()
        update_comp_form = CompetitionCreationForm(instance=competition)
        submission_form = SubmissionForm()
        team_enroll_form = TeamEnrollForm()
        team_invite_limit = competition.team_size_limit - (user_team.members.count() if user_team else 0)
        team_invite_form = TeamInviteForm(team_invite_limit=team_invite_limit) if team_invite_limit != 0 else None
        return render(request, 'judgy/competition_code.html', {
            'competition': competition,
            'user_team': user_team,
            'teams': teams,
            'problem_form': problem_form,
            'update_comp_form': update_comp_form,
            'submission_form': submission_form,
            'team_enroll_form': team_enroll_form,
            'team_invite_form': team_invite_form,
            'problems': problems,
            'download': competition.start <= timezone.now(),
            'upload': competition.start <= timezone.now() < competition.end and user_team,
            'enroll': competition.enroll_start <= timezone.now() < competition.enroll_end,
            'is_competition_over': competition.end <= timezone.now()
        })

    if request.method == 'DELETE':
        if request.user.is_superuser:
            competition.delete()
            return JsonResponse({})
        else:
            print('User is not authenticated and is not a super user. Competition not deleted.')

@user_passes_test(lambda u: u.is_superuser)
def problems_update_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == 'POST':
        problem_form = ProblemForm(request.POST, request.FILES)
        if (problem_form.is_valid()):
            problem = problem_form.save(commit=False)
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
     
            create_images_task.delay(code)

            return redirect('judgy:competition_code', code=competition.code)
        else:
            print('form.errors:\n', problem_form.errors)

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
                    team_add_user(competition, team, request.user)
                else:
                    for member in team.members.all():
                        user = member
                        body = f'Hi {member.first_name}, {request.user} wants to join your team "{team.name}" for the competition "{competition.name}".'
                        TeamJoinNotification.objects.create(user=user, body=body, request_user=request.user, team=team)
                return redirect('judgy:team_name', code=team.competition.code, name=team.name)
            else:
                print('Some field was not correctly filled.')
                print('form.errors:\n', form.errors)

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
        team_add_user(competition, team, notification.request_user)
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
                        user = User.objects.filter(email=email).first()
                        if user:
                            body = f'Hi {user.first_name}, {request.user} has invited you to join the team "{team.name}" for the competition "{competition.name}".'
                            TeamInviteNotification.objects.create(user=user, body=body, team=team)
                return redirect('judgy:team_name', code=team.competition.code, name=team.name)
            else:
                print('Some field was incorrectly filled out.')
                print('form.errors:\n', form.errors)

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
        team_add_user(competition, team, request.user)
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
    update_comp_form = CompetitionCreationForm(instance=competition)

    return render(request, 'judgy/team_name.html', {
        'competition': competition,
        'user_team': user_team,
        'team': team,
        'teams': teams,
        'enroll': competition.enroll_start <= timezone.now() < competition.enroll_end,
        'update_comp_form': update_comp_form,
        'team_enroll_form': team_enroll_form,
        'team_invite_form': team_invite_form
    })

def competitions_view(request):
    return JsonResponse(list(Competition.objects.all().values()), safe=False)

def download_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)

    if competition.start <= timezone.now():
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

@verified_required
def submit_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)
    problem = get_object_or_404(Problem, competition=competition, name=problem_name)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None

    if request.method == 'POST':
        if competition.start <= timezone.now() < competition.end and user_team:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                files = request.FILES.getlist('files')
                score_file, output_file = run_submission(code, problem_name, user_team, request.user, files)
                request.session['output_dir'] = str(output_file)
                
                with open(score_file, 'r') as f:
                    score = f.read()
                score = score.split(' ')[0]

                if problem.show_output:
                    output_url = f'/competition/{code}/{problem_name}/submission/output'
                    body = format_html(
                        'You got a score of {} in the problem "{}" for the competition "{}".<br>'
                        'Click <a href="{}" target="_blank">here</a> to see the output.',
                        score,
                        problem.name,
                        competition.name,
                        output_url
                    )
                else:
                    body=f'You got a score of {score} in the problem "{problem.name}" for the competition "{competition.name}".'

                Notification.objects.create(
                    user=request.user,
                    header='Your Score',
                    body=body,
                )

                competition_submissions = Submission.objects.filter(problem=problem)
                if problem.score_preference: # Higher Score is Better
                    competition_best_score = competition_submissions.aggregate(Max('score'))['score__max'] or -math.inf
                    if int(score) > competition_best_score:
                        superusers = User.objects.filter(is_superuser=True)
                        participants = User.objects.filter(teams__competition=competition)
                        header = 'New Best Score'
                        body = f'{request.user.first_name} from team "{user_team}" has achieved a new best score of {score} in the problem "{problem.name}" for the competition "{competition.name}"!'
                        for user in superusers:
                            Notification.objects.create(user=user, header=header, body=body)
                        for user in participants:
                            Notification.objects.create(user=user, header=header, body=body)
                else: # Lower Score is Better
                    competition_best_score = competition_submissions.aggregate(Min('score'))['score__min'] or +math.inf
                    if int(score) < competition_best_score:
                        superusers = User.objects.filter(is_superuser=True)
                        participants = User.objects.filter(teams__competition=competition)
                        header = 'New Best Score',
                        body = f'{request.user.first_name} from team "{user_team}" has achieved a new best score of {score} in the problem "{problem.name}" for the competition "{competition.name}"!'
                        for user in superusers:
                            Notification.objects.create(user=user, header=header, body=body)
                        for user in participants:
                            Notification.objects.create(user=user, header=header, body=body)

                Submission.objects.create(problem=problem, team=user_team, user=request.user, score=score)

                return redirect('judgy:competition_code', code=code)
            else:
                print('Some field was incorrectly filled out.')
                print('form.errors:\n', form.errors)


@verified_required
def output_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)
    problem = get_object_or_404(Problem, competition=competition, name=problem_name)

    with open(str(request.session.get('output_dir')), 'r') as f:
        output_data = f.read()

    return render(request, 'judgy/submission_output.html', {
        'problem': problem,
        'competition': competition,
        'output_data': output_data,
    })

def rankings_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    problems = Problem.objects.filter(competition=competition)
    teams = Team.objects.filter(competition=competition)

    rankings = []
    score_map = {problem.name: [] for problem in problems}
    time_list = []

    for team in teams:
        team_data = {
            'team_name': team.name,
            'total_attempt': 0,
            'total_time': timedelta(0)
        }
        
        for problem in problems:
            # Get submissions for the current problem and team
            submissions = Submission.objects.filter(problem=problem, team=team)
            
            # Determine the best submission based on score preference
            if problem.score_preference: # Higher Score is better
                best_submission = submissions.order_by('-score', 'time').first()
            else: # Lower Score is better
                best_submission = submissions.order_by('score', 'time').first()
            
            if best_submission:
                best_score = best_submission.score
                best_time = best_submission.time - competition.start
                team_data['total_attempt'] += 1
            else:
                # Assign default values for no submissions
                best_score = -math.inf if problem.score_preference else +math.inf
                best_time = competition.end - competition.start
            
            team_data[problem.name] = {'best_score': best_score, 'best_time': best_time}
            score_map[problem.name].append(best_score)
            team_data['total_time'] += best_time

        rankings.append(team_data)
        time_list.append(team_data['total_time'])

    # Assign ranks for each problem based on best score
    for problem in problems:
        scores = score_map[problem.name]
        ranked_scores = sorted(set(scores), reverse=problem.score_preference)
        
        for team in rankings:
            team[problem.name]['score_rank'] = ranked_scores.index(team[problem.name]['best_score']) + 1
    
    for team in rankings:
        team['total_score'] = sum(
            team[problem.name]['score_rank'] for problem in problems
        )

    # Clean up infinite scores
    for team in rankings:
        for problem in problems:
            score = team[problem.name]['best_score']
            team[problem.name]['best_score'] = score if math.isfinite(score) else None

    # Assign ranks based on total attempt
    ranked_attempts = sorted(set(team['total_attempt'] for team in rankings), reverse=True)
    
    for team in rankings:
        team['attempt_rank'] = ranked_attempts.index(team['total_attempt']) + 1

    # Assign ranks based on total score
    ranked_scores = sorted(set(team['total_score'] for team in rankings))
    
    for team in rankings:
        team['score_rank'] = ranked_scores.index(team['total_score']) + 1

    # Assign ranks based on total time
    ranked_times = sorted(set(time_list))

    for team in rankings:
        team['time_rank'] = ranked_times.index(team['total_time']) + 1

    # Finalize team rankings
    rankings.sort(key=lambda team: (
        team['attempt_rank'],
        team['score_rank'],
        team['time_rank'],
        team['team_name']
    ))

    rank = 1
    for i, team in enumerate(rankings):
        if i > 0:
            prev_team = rankings[i - 1]
            is_tied = (
                team['attempt_rank'] == prev_team['attempt_rank'] and
                team['score_rank'] == prev_team['score_rank'] and
                team['time_rank'] == prev_team['time_rank']
            )
            if not is_tied:
                rank = i + 1
        team['rank'] = rank

    return JsonResponse([{
        'rank': team['rank'],
        'team_name': team['team_name'],
        'attempt_rank': team['attempt_rank'],
        'score_rank': team['score_rank'],
        'time_rank': team['time_rank'],
        'total_attempt': team['total_attempt'],
        'total_score': team['total_score'],
        'total_time': team['total_time'],
        **{f'{problem.name}': {
            'score_rank': team[problem.name]['score_rank'],
            'best_score': team[problem.name]['best_score'],
            'best_time': team[problem.name]['best_time']
        } for problem in problems}
    } for team in rankings], safe=False)

def get_members_view(request, code, name):
    competition = get_object_or_404(Competition, code=code)
    team = get_object_or_404(Team, competition=competition, name=name)

    return JsonResponse(list(team.members.all().values()), safe=False)

# Class for updating a competition
class CompUpdate(APIView):
    def put(self, request, code):
        
        competition = get_object_or_404(Competition, code=code)
        
        serializer = CompSerializer(competition, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            redirect_url = reverse("judgy:competition_code", kwargs={"code":code})
            return Response({"success": f"Competition {competition.name} updated successfully!", "redirect_url": redirect_url}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
