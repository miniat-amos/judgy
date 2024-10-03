import logging
from django.conf import settings
from pathlib import Path

def create_user_dir(passed_in_dir, current_user):
    if not hasattr(current_user, 'id') or not current_user.id:
        raise ValueError("The current user must have a valid ID.")

    main_directory = Path(settings.BASE_DIR) / passed_in_dir
    
    try:
        # Ensure the submissions directory exists
        main_directory.mkdir(exist_ok=True)

        # Define and create the user-specific directory
        user_dir = main_directory / str(current_user.email)
        user_dir.mkdir(exist_ok=True)

        logging.info(f"Created directory: {user_dir}")
        return str(user_dir)

    except OSError as e:
        logging.error(f"Error creating directory {user_dir}: {e}")
        raise


def make_output_file(output_dir, file_name="output.txt"):
    output_file = Path(output_dir) / file_name
    output_file.touch(exist_ok=True)
    return output_file



    