import logging
import os
from django.conf import settings
from pathlib import Path

parent_dir = Path(settings.BASE_DIR).parent


def make_file(passed_in_dir, file_name):
    new_file = Path(passed_in_dir) / file_name
    new_file.touch(exist_ok=True)
    new_file.open("w").close()
    return new_file


def create_comp_dir(comp_code):
    main_directory = parent_dir / "competitions"
    main_directory.mkdir(exist_ok=True)

    comp_directory = main_directory / comp_code.lower()
    comp_directory.mkdir(exist_ok=True)

def create_problem_dir(problem_name, comp_code):
    main_directory = parent_dir / "competitions"
    comp_directory = main_directory / comp_code.lower()

    problems_directory = comp_directory / "problems"
    problems_directory.mkdir(exist_ok=True)

    problem = problems_directory / problem_name
    problem.mkdir(exist_ok=True)

    return problem.resolve()


def save_problem_files(problem_dir, directories, file_names, files):
    for i, file in enumerate(files):
        target_dir = problem_dir / directories[i]
        target_dir.mkdir(exist_ok=True)

        file_path = target_dir / file_names[i]
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)


def create_user_dir(passed_in_dir, current_user):
    if not hasattr(current_user, "id") or not current_user.id:
        raise ValueError("The current user must have a valid ID.")

    main_directory = Path(settings.BASE_DIR) / passed_in_dir

    try:
        main_directory.mkdir(exist_ok=True)

        # Define and create the user-specific directory
        user_directory = main_directory / str(current_user.email)
        user_directory.mkdir(exist_ok=True)

        logging.info(f"Created directory: {user_directory}")
        return str(user_directory)

    except OSError as e:
        logging.error(f"Error creating directory {user_directory}: {e}")
        raise
