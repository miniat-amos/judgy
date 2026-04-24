import math
import os
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

parent_dir = Path("/data")


def make_file(dir, file, owner_ship=0):
    new_file = Path(dir) / file
    new_file.touch(exist_ok=True)
    
    if owner_ship:
        os.chown(new_file, owner_ship, owner_ship)
        
    return new_file

def create_comp_dir(code):
    comp_directory = parent_dir / 'competitions' / code.lower()
    comp_directory.mkdir(parents=True, exist_ok=True)
    
    return comp_directory.resolve()
    
def get_comp_dir(code):
    comp_directory = parent_dir / 'competitions' / code.lower()

    return comp_directory.resolve()

def get_problem_dir(code, problem):
    comp_directory = get_comp_dir(code)
        
    problem_directory = comp_directory / 'problems' / problem
    
    return problem_directory.resolve()
    

def get_user_submission_dir(code, team, user, problem, submission):

    problem_directory = get_problem_dir(code, problem)    
    
    submissions_directory = problem_directory / 'submissions'
    
    team_directory = submissions_directory / slugify(str(team))
    
    user_directory = team_directory / user
    
    submission_directory = user_directory / submission
    
    return submission_directory.resolve()


def create_problem_dir(code, problem_name, description, judging_program, other_files, dist_files):
    comp_directory = create_comp_dir(code)

    problems_directory = comp_directory / 'problems'
    problems_directory.mkdir(exist_ok=True)

    problem = problems_directory / problem_name
    problem.mkdir(exist_ok=True)
    
    submissions = problem / "submissions"
    submissions.mkdir(exist_ok=True)
    
    create_problem_description_dir(problem, description)
    create_judging_prog_dir(problem, judging_program)
    create_other_files_dir(problem, other_files)
    create_problem_dist_dir(problem, dist_files)

   
def create_problem_description_dir(problem, description):
    description_dir = problem / 'problem_description'
    description_dir.mkdir(exist_ok=True)
    
    with open(description_dir / description.name, 'wb') as f:
        for chunk in description.chunks():
            f.write(chunk)

def create_judging_prog_dir(problem, judging_program):
    judging_prog_dir = problem / 'judging_program'
    judging_prog_dir.mkdir(exist_ok=True)
    
    if judging_program:
        with open(judging_prog_dir / judging_program.name, 'wb') as f:
            for chunk in judging_program.chunks():
                f.write(chunk)

def create_other_files_dir(problem, other_files):
    other_files_dir = problem / 'other_files'
    other_files_dir.mkdir(exist_ok=True)
    
    for file in other_files:
        with open(other_files_dir / file.name, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
    
def create_problem_dist_dir(problem, dist_files):
    dist_dir = problem / 'dist'
    dist_dir.mkdir(exist_ok=True)
    
    for file in dist_files:
        with open(dist_dir / file.name, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)
                
    
def create_user_dirs(code, user, problem, team, submission=None):
  
    comp_directory = get_comp_dir(code)
    submissions_directory = comp_directory / "problems" / str(problem) / "submissions"
    
    team_name = slugify(str(team.name))
    user_directory = submissions_directory / team_name / str(user.email)
    user_directory.mkdir(parents=True, exist_ok=True)

    submission_directory = user_directory / str(submission.id)
    submission_directory.mkdir(exist_ok=True)

    output_directory = user_directory / "output"

    submission_directory.mkdir(exist_ok=True)
    output_directory.mkdir(exist_ok=True)

    os.chown(output_directory, 1001, 1001)

    return {
        "submission_dir": str(submission_directory.resolve()),
        "output_dir": str(output_directory.resolve())
    }
    
    
def create_formatted_name(vars: list, delimiter: str) -> str:
    
    formatted_name = ""
         
    for index, var in enumerate(vars):
        if index == len(vars) - 1:
            formatted_name = formatted_name + str(var)
        else:
            var = str(var) + str(delimiter)
            formatted_name = formatted_name + var
    
    return formatted_name
        
    
def store_user_submission(files, submission_dir, user, problem_name, code):
    submitted_files = []
    
    submission_dir = Path(submission_dir)
    
    for uploaded_file in files:
        
        ext = Path(uploaded_file.name).suffix
        
        email = user.email.split('@')[0]
        formatted_name = [email, problem_name.replace(' ', '-'), code.lower()]
        uploaded_file.name = create_formatted_name(formatted_name, "-")
                
        file_path = submission_dir / (uploaded_file.name + ext)
        
        
        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        submitted_files.append(file_path.resolve())

    return [str(p) for p in submitted_files]



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

            if best_submission and best_submission.score is not None:
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
            
            if score == None:
                team[problem.name]["best_score"] = None 
            elif math.isfinite(score):
                team[problem.name]["best_score"] = score 
                
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
                    "best_score": str(team[problem.name]["best_score"]),
                    "best_time": team[problem.name]["best_time"],
                }
                for problem in problems
            },
        }
        for team in rankings
    ]


channel_layer = get_channel_layer()

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


