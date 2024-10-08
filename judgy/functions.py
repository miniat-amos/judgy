import os
import docker
from .utils import make_file, create_user_dir
from django.conf import settings
from pathlib import Path

languages = {
    ".py": {"image": "python", "type": "interpreted", "interpreter": "python3"},
    ".js": {"image": "node", "type": "interpreted", "interpreter": "node"},
    ".rb": {"image": "ruby", "type": "interpreted", "interpreter": "ruby"},
    ".c": {"image": "gcc", "type": "compiled", "compiler": "gcc"},
    ".cpp": {"image": "gcc", "type": "compiled", "compiler": "g++"},
}


def start_containers(f, current_user):
    # Variables for local machine
    
    # Get file extension
    file_extension = os.path.splitext(f.name)[1]
    submitted_image = languages[file_extension]["image"]

    # Make submissions dir
    submissions_dir = create_user_dir("submissions", current_user)

    # Store file in submissions dir
    submitted_file = os.path.join(submissions_dir, f.name)
    with open(submitted_file, "wb+") as destination:
        for chunk in f.chunks():
            # Looping over UploadedFile.chunks() instead of using read()
            # ensures that large files don’t overwhelm your system’s memory.
            destination.write(chunk)

    # Create output directory
    output_dir = create_user_dir("outputs", current_user)
    output_file = make_file(output_dir, "output.txt")
    score_file = make_file(output_dir, "score.txt")

    # Connect to docker daemon
    client = docker.from_env()

    # Variables for container
    docker_image = f"judgy-{submitted_image}_app"
    container_name = f"{submitted_image}_container"
    container_main_directory = "/usr/app"
    container_user_file = os.path.join(container_main_directory, f.name)  
    container_output_directory = os.path.join(container_main_directory, "outputs")
    container_output_path = os.path.join(container_output_directory, "output.txt")
    container_score_path = os.path.join(container_output_directory, "score.txt")
    volumes = {
        submitted_file: {"bind": container_user_file, "mode": "rw"},
        output_file: {
            "bind": container_output_path,
            "mode": "rw",
    },
        score_file: {
            "bind": container_score_path,
            "mode": "rw",
    },
}
    
    if languages[file_extension]["type"] == "interpreted":
        interpreter = languages[file_extension]["interpreter"]
        container = client.containers.run(
            docker_image,
            command=f"""
                bash -c '{interpreter} {container_user_file} > {container_output_path} && python3 judge.py mine.dat {interpreter} {container_user_file} > {container_score_path}'
                """,
            volumes=volumes,
            detach=True,
            name=container_name,
        )

    elif languages[file_extension]["type"] == "compiled":
        compiler = languages[file_extension]["compiler"]
        container = client.containers.run(
            docker_image,
            command=f"""
                    bash -c '{compiler} {container_user_file} -o {container_main_directory}/a.out && ({container_main_directory}/a.out) > {container_output_path} && python3 judge.py mine.dat {container_main_directory}/a.out > {container_score_path}'
                    """,
            volumes=volumes,
            detach=True,
            name=container_name,
        )

    container.stop()
    container.remove()
    
    return output_file, score_file
