import math
import os
import shutil
from django.db.models import Min, Max
from datetime import timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from pathlib import Path
from judgy.models import (
    User
)
from competition.models import (
    Problem,
    Submission,
    Team,
)
from notifications.models import (
    Notification
)

parent_dir = Path(settings.BASE_DIR).parent

def make_file(dir, file):
    new_file = Path(dir) / file
    new_file.touch(exist_ok=True)
    new_file.open('w').close()
    return new_file

def create_comp_dir(code):
    main_directory = parent_dir / 'competitions'
    main_directory.mkdir(exist_ok=True)

    comp_directory = main_directory / code.lower()
    comp_directory.mkdir(exist_ok=True)
    
def get_dist_dir(code, problem):
    main_directory = parent_dir / 'competitions'
    
    comp_directory = main_directory / code.lower()
        
    problem_directory = comp_directory / 'problems' / problem
    
    distributed_directory = problem_directory / 'dist'
        
    return distributed_directory.resolve()

def get_submission_dir(code, team, user, problem, submission):
    main_directory = parent_dir / 'competitions'
    
    comp_directory = main_directory / code.lower()
        
    problem_directory = comp_directory / 'problems' / problem
    
    submissions_directory = problem_directory / 'submissions'
    
    team_directory = submissions_directory / team
    
    user_directory = team_directory / user
    
    submission_directory = user_directory / submission
    
    return submission_directory.resolve()
        


def create_problem(code, name, description, judge_py, other_files, dist):
    main_directory = parent_dir / 'competitions'
    comp_directory = main_directory / code.lower()

    problems_directory = comp_directory / 'problems'
    problems_directory.mkdir(exist_ok=True)

    problem = problems_directory / name
    problem.mkdir(exist_ok=True)
    
    submissions = problem / "submissions"
    submissions.mkdir(exist_ok=True)
    
    dist_dir = problem / 'dist'
    dist_dir.mkdir(exist_ok=True)

    description_dir = problem / 'problem_description'
    description_dir.mkdir(exist_ok=True)

    with open(description_dir / description.name, 'wb') as f:
        for chunk in description.chunks():
            f.write(chunk)
    if description.name in dist:
        with open(dist_dir / description.name, 'wb') as f:
            for chunk in description.chunks():
                f.write(chunk)

    judge_py_dir = problem / 'judging_program'
    judge_py_dir.mkdir(exist_ok=True)

    if(judge_py):
        with open(judge_py_dir / judge_py.name, 'wb') as f:
            for chunk in judge_py.chunks():
                f.write(chunk)
        if judge_py.name in dist:
            with open(dist_dir / judge_py.name, 'wb') as f:
                for chunk in judge_py.chunks():
                    f.write(chunk)
    
    other_files_dir = problem / 'other_files'
    other_files_dir.mkdir(exist_ok=True)

    for file in other_files:
        with open(other_files_dir / file.name, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
        if file.name in dist:
            with open(dist_dir / file.name, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)

def create_user_dir(code, user, problem, team, submission = None, subjective = False):
    main_directory = parent_dir / 'competitions'
    comp_directory = main_directory / code.lower()
    submissions_directory = comp_directory / 'problems' / problem / 'submissions'

    team_name = slugify(str(team.name))
    user_directory = submissions_directory / team_name / str(user.email) 
    user_directory.mkdir(parents=True, exist_ok=True)

    if subjective:
   
        # Create new submission folder
        submission_directory = user_directory / f"{submission.id}"
        submission_directory.mkdir(exist_ok=True)

        return submission_directory.resolve()
    
    else:
        submission_directory = user_directory / 'submission'
        submission_directory.mkdir(exist_ok=True)

        output_directory = user_directory / 'output'
        output_directory.mkdir(exist_ok=True)

        return submission_directory.resolve(), output_directory.resolve()


def team_add_user(competition, team, user):
    current_team = Team.objects.filter(competition=competition, members=user).first()
    if current_team:
        current_team.members.remove(user)
        if current_team.members.count():
            for member in current_team.members.all():
                Notification.objects.create(
                    user=member,
                    header='Update',
                    body=f'{user} left the team.'
                )
        else:
            current_team.delete()
    team.members.add(user)


def make_temp_dir(user):
    main_directory = Path('/tmp')
    temp_dir = main_directory / 'judgy_tmp'
    temp_dir.mkdir(exist_ok=True)
    
    user_temp_dir = temp_dir / str(user.email)
    user_temp_dir.mkdir(exist_ok=True)
    
    return user_temp_dir.resolve()

channel_layer = get_channel_layer()

def _format_timedelta(value):
    if value is None:
        return None
    if isinstance(value, timedelta):
        return str(value)
    return value


def calculate_rankings(competition):
    problems = Problem.objects.filter(competition=competition).order_by("number")
    teams = (
        Team.objects.filter(competition=competition)
        .prefetch_related("members")
        .order_by("name")
    )

    rankings = []
    score_map = {problem.name: [] for problem in problems}
    time_list = []

    for team in teams:
        team_data = {
            "team_id": team.id,
            "team_name": team.name,
            "members": [member.first_name for member in team.members.all()],
            "total_attempt": 0,
            "total_time": timedelta(0),
        }

        for problem in problems:
            submissions = Submission.objects.filter(problem=problem, team=team)

            if problem.score_preference:
                best_submission = submissions.order_by("-score", "time").first()
            else:
                best_submission = submissions.order_by("score", "time").first()

            if best_submission:
                best_score = best_submission.score
                best_time = best_submission.time - competition.start
                team_data["total_attempt"] += 1
            else:
                best_score = -math.inf if problem.score_preference else math.inf
                best_time = competition.end - competition.start

            team_data[problem.name] = {
                "best_score": best_score,
                "best_time": best_time,
            }
            score_map[problem.name].append(best_score)
            team_data["total_time"] += best_time

        rankings.append(team_data)
        time_list.append(team_data["total_time"])

    for problem in problems:
        scores = score_map[problem.name]
        ranked_scores = sorted(set(scores), reverse=problem.score_preference)

        for team in rankings:
            team[problem.name]["score_rank"] = (
                ranked_scores.index(team[problem.name]["best_score"]) + 1
            )

    for team in rankings:
        team["total_score"] = sum(
            team[problem.name]["score_rank"] for problem in problems
        )

    for team in rankings:
        for problem in problems:
            score = team[problem.name]["best_score"]
            team[problem.name]["best_score"] = score if math.isfinite(score) else None
            team[problem.name]["best_time"] = _format_timedelta(
                team[problem.name]["best_time"]
            )

    ranked_attempts = sorted(
        set(team["total_attempt"] for team in rankings), reverse=True
    )

    for team in rankings:
        team["attempt_rank"] = ranked_attempts.index(team["total_attempt"]) + 1

    ranked_scores = sorted(set(team["total_score"] for team in rankings))

    for team in rankings:
        team["score_rank"] = ranked_scores.index(team["total_score"]) + 1

    ranked_times = sorted(set(time_list))

    for team in rankings:
        team["time_rank"] = ranked_times.index(team["total_time"]) + 1
        team["total_time"] = _format_timedelta(team["total_time"])

    rankings.sort(
        key=lambda team: (
            team["attempt_rank"],
            team["score_rank"],
            team["time_rank"],
            team["team_name"],
        )
    )

    rank = 1
    for index, team in enumerate(rankings):
        if index > 0:
            prev_team = rankings[index - 1]
            is_tied = (
                team["attempt_rank"] == prev_team["attempt_rank"]
                and team["score_rank"] == prev_team["score_rank"]
                and team["time_rank"] == prev_team["time_rank"]
            )
            if not is_tied:
                rank = index + 1
        team["rank"] = rank

    return [
        {
            "rank": team["rank"],
            "team_id": team["team_id"],
            "team_name": team["team_name"],
            "members": team["members"],
            "attempt_rank": team["attempt_rank"],
            "score_rank": team["score_rank"],
            "time_rank": team["time_rank"],
            "total_attempt": team["total_attempt"],
            "total_score": team["total_score"],
            "total_time": team["total_time"],
            **{
                f"{problem.name}": {
                    "score_rank": team[problem.name]["score_rank"],
                    "best_score": team[problem.name]["best_score"],
                    "best_time": team[problem.name]["best_time"],
                }
                for problem in problems
            },
        }
        for team in rankings
    ]

def store_submissions(files, submission_dir):
    submitted_files = []
    for file_path_str in files:  # files is now a list of strings
        file_path = Path(submission_dir) / Path(file_path_str).name
        # If you need to copy the file to submission_dir
        with open(file_path_str, "rb") as source_file:
            with open(file_path, "wb") as destination_file:
                destination_file.write(source_file.read())
        submitted_files.append(file_path)  # Track all file paths

    return submitted_files


def overwrite_submission_dirfiles(submission_dir):
    if os.path.exists(submission_dir):
        # Loop through each item in the directory
            for item in os.listdir(submission_dir):
                item_path = os.path.join(submission_dir, item)
                # Check if it's a file or directory and remove accordingly
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)  # Remove file or symbolic link
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

def send_competition_best(problem, competition_best):

    async_to_sync(channel_layer.group_send)(
        f"competition_{problem.competition.code}",
        {
            "type": "score_update",
            "data": {
                "problem": problem.id,
                "competition_best": competition_best,
            }
        }
    )

def send_team_best(problem, team, team_best):

    async_to_sync(channel_layer.group_send)(
        f"team_{team.id}",
        {
            "type": "score_update",
            "data": {
                "problem": problem.id,
                "team_best": team_best,
            }
        }
    )
    
def send_user_best(problem, user, user_best):

    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "score_update",
            "data": {
                "problem": problem.id,
                "user_best": user_best,
            }
        }
    )
    
def send_rankings_update(competition):
    rankings = calculate_rankings(competition)
    async_to_sync(channel_layer.group_send)(
        f"competition_{competition.code}",
        {
            "type": "rankings_update",
            "data": {
                "rankings": rankings,
            },
        },
    )

def check_competition_best(competition, problem, score, user, user_team):
    competition_submissions = Submission.objects.filter(problem=problem)
    if problem.score_preference:
        competition_best_score = competition_submissions.aggregate(Max('score'))['score__max'] or -math.inf
        if int(score) > competition_best_score:
            notify_best_score(competition, user, user_team, score, problem)
    else:
        competition_best_score = competition_submissions.aggregate(Min('score'))['score__min'] or +math.inf
        if int(score) < competition_best_score:
            notify_best_score(competition, user, user_team, score, problem)

def notify_best_score(competition, user, team, score, problem):
    superusers = User.objects.filter(is_superuser=True)
    participants = User.objects.filter(teams__competition=competition)
    header = 'New Best Score'
    body = f'"{user.first_name}" from team "{team.name}" has achieved a new best score of {score} in "{problem.name}" for competition "{competition.name}"!'
    for user in superusers:
        Notification.objects.create(user=user, header=header, body=body)
    for user in participants:
        Notification.objects.create(user=user, header=header, body=body)
    

def notify_admin_submission(competition, user, team, problem):
    superusers = User.objects.filter(is_superuser=True)
    header = 'New Submission'
    admin_team_interface = reverse('competition:admin_team_interface', kwargs={'code': competition.code, 'name': team.name})
    body = (
            f'"{user.first_name}" from team "{team.name}" '
            f'has sent a new submission for "{problem.name}" ' 
            f'for competition "{competition.name}"! '
            f'See <a href="{admin_team_interface}" target="_blank">here</a>'
            )
    
    for user in superusers:
        Notification.objects.create(user=user, header=header, body=body)


