import os
from django.conf import settings
from pathlib import Path

def create_directory(directory_name):
    dir_path = os.path.join(settings.BASE_DIR, directory_name)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def get_output_file(output_dir="outputs", file_name="output.txt"):
    output_directory = create_directory(output_dir)
    output_file = Path(output_directory) / file_name
    output_file.touch(exist_ok=True)
    return output_file