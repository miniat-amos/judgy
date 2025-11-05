from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils.text import slugify
from pathlib import Path
from competition.models import (
  Team
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

def create_user_dir(code, user, problem, team):
    main_directory = parent_dir / 'competitions'
    comp_directory = main_directory / code.lower()
    submissions_directory = comp_directory / 'problems' / problem / 'submissions'

    team_name = slugify(str(team.name))
    user_directory = submissions_directory / team_name / str(user.email) 
    user_directory.mkdir(parents=True, exist_ok=True)

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

def send_competition_best(problem, competition_best):

        # Competition best
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

        # Competition best
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
