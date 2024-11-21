import docker
import os
import subprocess
import shutil
from django.conf import settings
from pathlib import Path
from .utils import make_file, create_user_dir

from docker.errors import ContainerError

languages = {
    ".py": {"image": "python", "type": "interpreted", "interpreter": "python3"},
    ".js": {"image": "node", "type": "interpreted", "interpreter": "node"},
    ".rb": {"image": "ruby", "type": "interpreted", "interpreter": "ruby"},
    ".c": {"image": "gcc", "type": "compiled", "compiler": "gcc"},
    ".cpp": {"image": "gcc", "type": "compiled", "compiler": "g++"},
    ".java": {"image": "java", "type": "compiled-and-interpreted", "compiler": "javac", "interpreter": "java"}
}

def run_submission(code, problem, team, user, files):
    # Variables for local machine
    # Get file extension
    file_extension = os.path.splitext(files[0].name)[1]
    submitted_image = languages[file_extension]["image"]

    # Make submissions dir
    submission_dir, output_dir = create_user_dir(code, user, problem, team)

    if os.path.exists(submission_dir):
    # Loop through each item in the directory
        for item in os.listdir(submission_dir):
            item_path = os.path.join(submission_dir, item)
            # Check if it's a file or directory and remove accordingly
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove file or symbolic link
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  

    # Store file in submissions dir
    submitted_files = []
    for file in files:
        file_path = Path(submission_dir) / file.name
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        submitted_files.append(file_path)  # Track all file paths

    # Create output directory
    score_file = make_file(output_dir, "score.txt")
    output_file = make_file(output_dir, "output.txt")

    client = docker.from_env()

    # Variables for container
    code = code.lower()
    docker_image = f"judgy-{code}-{submitted_image}_app"
    container_name = f"{submitted_image}_{user.first_name}_container"
    container_main_directory = Path("/app")    
    container_score_path = container_main_directory / "outputs" / "score.txt"
    container_output_path = container_main_directory / "outputs" / "output.txt"

    # Volumes for file-to-file binding
    volumes = {
        str(score_file): {"bind": str(container_score_path), "mode": "rw"},
        str(output_file): {"bind": str(container_output_path), "mode": "rw"}
    }

    if all(file.name.endswith(".java") for file in submitted_files):
        # If all files are Java, bind all of them
        for submitted_file in submitted_files:
            container_user_file = container_main_directory / problem / submitted_file.name
            volumes[str(submitted_file)] = {"bind": str(container_user_file), "mode": "rw"}
    else:
        # If not all files are Java, only bind the first file
        first_file = submitted_files[0]
        container_user_file = container_main_directory / problem / first_file.name
        volumes[str(first_file)] = {"bind": str(container_user_file), "mode": "rw"}
        
    
    if languages[file_extension]["type"] == "compiled-and-interpreted":
        # Directory where Java files are stored in the container
        interpreter = languages[file_extension]["interpreter"]
        compiler = languages[file_extension]["compiler"]
            
        def find_main_file():
            for f in submitted_files:
                with open(f, 'r') as file:
                    content = file.read()
                    if 'public static void main(String[] args)' in content:
                        return container_main_directory / problem / f.name
            return None

        def classes_string():
            file_paths = [str(container_main_directory / problem / f.name) for f in submitted_files]
            return " ".join(file_paths)


        main_file = find_main_file()
        classes = classes_string()
                
        command = [
            "bash", "-c",
            f"cd /app/{problem} && {compiler} {classes} && python3 judge.py {interpreter} {main_file.stem} > {container_score_path} && cat run_* > {container_output_path}"
        ]
        
    elif languages[file_extension]["type"] == "interpreted":
        interpreter = languages[file_extension]["interpreter"]
        command=f'bash -c "cd /app/{problem}/ && python3 judge.py {interpreter} {container_user_file} > {container_score_path} && cat run_* > {container_output_path}"'

    elif languages[file_extension]["type"] == "compiled":
        compiler = languages[file_extension]["compiler"]
        command=f'bash -c "cd /app/{problem}/ && {compiler} {container_user_file} -o a.out && python3 judge.py ./a.out > {container_score_path} && cat run_* > {container_output_path}"'
    
    container = client.containers.run(
        docker_image,
        command=command,
        volumes=volumes,
        detach=True,
        name=container_name,
    )

    container.stop()
    container.remove()
        
    return score_file, output_file

# Create Docker images based on the competition code
# Preloads all Docker images with problem files
def create_images(competition_code):
    docker_image_script = Path(settings.BASE_DIR) / "docker_setup.sh"
    subprocess.run(f"bash {docker_image_script} {competition_code.lower()}", shell=True)
