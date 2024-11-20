import logging
from django.conf import settings
from pathlib import Path

parent_dir = Path(settings.BASE_DIR).parent

def make_file(passed_in_dir, file_name):
    new_file = Path(passed_in_dir) / file_name
    new_file.touch(exist_ok=True)
    new_file.open('w').close()
    return new_file

def create_comp_dir(code):
    main_directory = parent_dir / 'competitions'
    main_directory.mkdir(exist_ok=True)

    comp_directory = main_directory / code.lower()
    comp_directory.mkdir(exist_ok=True)
    
def get_dist_dir(code, problem_name):
    main_directory = parent_dir / 'competitions'
    
    comp_directory = main_directory / code.lower()
    
    problem_directory = comp_directory / problem_name
    
    distributed_directory = problem_directory / "dist"
    
    return distributed_directory.resolve()



def create_problem(code, name, description, judge_py, other_files, dist):
    main_directory = parent_dir / 'competitions'
    comp_directory = main_directory / code.lower()

    problems_directory = comp_directory / 'problems'
    problems_directory.mkdir(exist_ok=True)

    problem = problems_directory / name
    problem.mkdir(exist_ok=True)

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

def create_user_dir(passed_in_dir, current_user):
    if not hasattr(current_user, 'id') or not current_user.id:
        raise ValueError('The current user must have a valid ID.')

    main_directory = Path(settings.BASE_DIR) / passed_in_dir

    try:
        main_directory.mkdir(exist_ok=True)

        user_directory = main_directory / str(current_user.email)
        user_directory.mkdir(exist_ok=True)

        logging.info(f'Created directory: {user_directory}')
        return str(user_directory)
    except OSError as e:
        logging.error(f'Error creating directory {user_directory}: {e}')
        raise
