import os
import docker
from .utils import make_output_file, create_user_dir
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
    # Get file extension
    file_extension = os.path.splitext(f.name)[1]
    submitted_image = languages[file_extension]["image"]

    # Make submissions dir
    submissions_dir = create_user_dir("submissions", current_user)

    # Store file in submissions dir
    input_file = os.path.join(submissions_dir, f.name)
    with open(input_file, "wb+") as destination:
        for chunk in f.chunks():
            # Looping over UploadedFile.chunks() instead of using read()
            # ensures that large files don’t overwhelm your system’s memory.
            destination.write(chunk)

    # Create output directory
    output_dir = create_user_dir("outputs", current_user)
    output_file = make_output_file(output_dir)

    # Connect to docker daemon
    client = docker.from_env()

    # Container variables
    image = f"judgy-{submitted_image}_app"
    container_name = f"{submitted_image}_container"
    container_directory = "/usr/app"
    container_output = "outputs"
    output_path = os.path.join(container_output, "output.txt")
    volumes = {
        input_file: {"bind": os.path.join(container_directory, f.name), "mode": "rw"},
        str(output_file.parent): {
            "bind": os.path.join(container_directory, container_output),
            "mode": "rw",
        },
    }

    if languages[file_extension]["type"] == "interpreted":
        interpreter = languages[file_extension]["interpreter"]
        container = client.containers.run(
            image,
            command=f"sh -c '{interpreter} {os.path.join(container_directory, f.name)} > {output_path}'",
            volumes=volumes,
            detach=True,
            name=container_name,
        )

    elif languages[file_extension]["type"] == "compiled":
        compiler = languages[file_extension]["compiler"]
        container = client.containers.run(
            image,
            command=f"sh -c '{compiler} {os.path.join(container_directory, f.name)} -o {container_directory}/a.out && {container_directory}/a.out > {output_path}'",
            volumes=volumes,
            detach=True,
            name=container_name,
        )

    container.stop()
    container.remove()
    
    return output_file
