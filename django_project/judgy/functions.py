import os
import docker
import subprocess
from .utils import make_file, create_user_dir
from django.conf import settings
from pathlib import Path

from docker.errors import ContainerError

languages = {
    ".py": {"image": "python", "type": "interpreted", "interpreter": "python3"},
    ".js": {"image": "node", "type": "interpreted", "interpreter": "node"},
    ".rb": {"image": "ruby", "type": "interpreted", "interpreter": "ruby"},
    ".c": {"image": "gcc", "type": "compiled", "compiler": "gcc"},
    ".cpp": {"image": "gcc", "type": "compiled", "compiler": "g++"},
    ".java": {"image": "java", "type": "compiled-and-interpreted", "compiler": "javac", "interpreter": "java",
}
}


def start_containers(f, current_user):
    # Variables for local machine
    # Get file extension
    file_extension = os.path.splitext(f[0].name)[1]
    submitted_image = languages[file_extension]["image"]

    # Make submissions dir
    submissions_dir = create_user_dir("submissions", current_user)

    # Store file in submissions dir
    submitted_files = []
    for file in f:
        file_path = Path(submissions_dir) / file.name
        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        submitted_files.append(file_path)  # Track all file paths


    # Create output directory
    output_dir = create_user_dir("outputs", current_user)
    output_file = make_file(output_dir, "output.txt")
    score_file = make_file(output_dir, "score.txt")

    client = docker.from_env()

    # Variables for container
    docker_image = f"judgy-92f5-{submitted_image}_app"
    container_name = f"{submitted_image}_{current_user.first_name}_container"
    container_main_directory = Path("/app")
    
    container_output_path = container_main_directory / "outputs" / "output.txt"
    container_score_path = container_main_directory / "outputs" / "score.txt"

    # Volumes for file-to-file binding
    volumes = {
        str(output_file): {"bind": str(container_output_path), "mode": "rw"},
        str(score_file): {"bind": str(container_score_path), "mode": "rw"},
    }

    for submitted_file in submitted_files:
        container_main_directory = Path("/usr/app")
        container_user_file = container_main_directory / submitted_file.name
        volumes[str(submitted_file)] = {"bind": str(container_user_file), "mode": "rw"}
    
    if languages[file_extension]["type"] == "compiled-and-interpreted":
        # Directory where Java files are stored in the container
        interpreter = languages[file_extension]["interpreter"]
        compiler = languages[file_extension]["compiler"]
            
        def find_main_file():
            for f in submitted_files:
                with open(f, 'r') as file:
                    content = file.read()
                    if 'public static void main(String[] args)' in content:
                        container_main_path = Path("/usr/app") / f.name
                        return container_main_path
            return None
        
        def classes_string():
            file_paths = []
            for f in submitted_files:
                file_path = Path("/usr/app") / f.name
                file_paths.append(str(file_path))
            return " ".join(file_paths)

        main_file = find_main_file()
        classes = classes_string()
        classpath = "/usr/app/"

        # Command to compile and execute the Java files
        container = client.containers.run(
            docker_image,
            command=f'bash -c "{compiler} {classes} && {interpreter} -cp {classpath} {main_file.stem} < /app/golddigger-mine.dat > {container_output_path} && python3 golddigger-judge.py golddigger-mine.dat {compiler} {classes} && {interpreter} -cp {classpath} {main_file.stem} > {container_score_path}"',
            volumes=volumes,
            detach=True,
            name=container_name,
        )
        
    elif languages[file_extension]["type"] == "interpreted":
        interpreter = languages[file_extension]["interpreter"]
        container = client.containers.run(
            docker_image,
            command=f'bash -c "{interpreter} {container_user_file} < /app/golddigger-mine.dat > {container_output_path} && python3 golddigger-judge.py golddigger-mine.dat {interpreter} {container_user_file} > {container_score_path}"',
            volumes=volumes,
            detach=True,
            name=container_name,
        )
    elif languages[file_extension]["type"] == "compiled":
        compiler = languages[file_extension]["compiler"]
        container = client.containers.run(
            docker_image,
            command=f'bash -c "{compiler} {container_user_file} -o {container_main_directory}/a.out && ({container_main_directory}/a.out) < mine.dat > {container_output_path} && python3 judge.py mine.dat {container_main_directory}/a.out > {container_score_path}"',
            volumes=volumes,
            detach=True,
            name=container_name,
        )

    container.stop()    
    container.remove()
        
    return output_file, score_file

# Create Docker images based on the competition code
# Preloads all Docker images with problem files
def create_images(competition_code):
    docker_image_script = Path(settings.BASE_DIR) / "docker_setup.sh"
    subprocess.run(f"bash {docker_image_script} {competition_code.lower()}", shell=True)
