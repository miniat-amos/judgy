import docker
import os
import shutil
from pathlib import Path
from judgy.utils import make_file, create_user_dir

languages = {
    ".py": {"image": "python", "type": "interpreted", "interpreter": "python3", "language": "Python"},
    ".js": {"image": "node", "type": "interpreted", "interpreter": "node", "language": "JavaScript"},
    ".rb": {"image": "ruby", "type": "interpreted", "interpreter": "ruby", "language": "Ruby"},
    ".c": {"image": "gcc", "type": "compiled", "compiler": "gcc", "language": "C"},
    ".cpp": {"image": "gcc", "type": "compiled", "compiler": "g++", "language": "C++"},
    ".java": {"image": "java", "type": "compiled-and-interpreted", "compiler": "javac", "interpreter": "java", "language": "Java"}
}

def run_submission(code, problem, team, user, files):
    # Variables for local machine
    # Get file extension
    file_extension = os.path.splitext(files[0])[1]
    submitted_image = languages[file_extension]["image"]
    language = languages[file_extension]["language"]
    
    problem_name = problem.name
    
    if problem.score_preference:
        timeout_score = -9223372036854775808
    else:
        timeout_score = 9223372036854775808

    
    # Make submissions dir
    submission_dir, output_dir = create_user_dir(code, user, problem_name, team)

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
    for file_path_str in files:  # files is now a list of strings
        file_path = Path(submission_dir) / Path(file_path_str).name
        # If you need to copy the file to submission_dir
        with open(file_path_str, "rb") as source_file:
            with open(file_path, "wb") as destination_file:
                destination_file.write(source_file.read())
        submitted_files.append(file_path)  # Track all file paths

    # Create output directory
    score_file = make_file(output_dir, "score.txt")
    output_file = make_file(output_dir, "output.txt")
    
    

    client = docker.from_env()

    # Variables for container
    code = code.lower()
    docker_image = f"judgy-{code}-{submitted_image}_app"
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
            container_user_file = container_main_directory / problem_name / submitted_file.name
            volumes[str(submitted_file)] = {"bind": str(container_user_file), "mode": "rw"}
    else:
        # If not all files are Java, only bind the first file
        first_file = submitted_files[0]
        container_user_file = container_main_directory / problem_name / first_file.name
        volumes[str(first_file)] = {"bind": str(container_user_file), "mode": "rw"}
        judgy_source_file = os.path.basename(container_user_file)
     
    if languages[file_extension]["type"] == "compiled-and-interpreted":
        # Directory where Java files are stored in the container
        interpreter = languages[file_extension]["interpreter"]
        compiler = languages[file_extension]["compiler"]
            
        def find_main_file():
            for f in submitted_files:
                with open(f, 'r') as file:
                    content = file.read()
                    if 'public static void main(String[] args)' in content:
                        file_name = f.name
                        return container_main_directory / problem_name / f.name
            return None

        def classes_list():
            return [str(container_main_directory / problem_name / f.name) for f in submitted_files]

        main_file = find_main_file()
        classes = classes_list()
        judgy_source_file = os.path.basename(main_file)
        command = (
            f'bash -c "cd \\"/app/{problem_name}\\" && '
            f'{compiler} ' + " ".join([f'\\"{cls}\\"' for cls in classes]) + '; '
            f'status=$?; '
            f'if [ $status -ne 0 ]; then '
            f'  echo {timeout_score} > {container_score_path}; '
            f'  echo Compilation failed > {container_output_path}; '
            f'  exit 1; '
            f'fi; '
            f'output=$(timeout 60s python3 judge.py {interpreter} \\"{main_file.stem}\\"); '
            f'status=$?; '
            f'if [ $status -eq 124 ]; then '
            f'  echo {timeout_score} > {container_score_path}; '
            f'  echo Your program timed out > {container_output_path}; '
            f'elif [ $status -ne 0 ]; then '
            f'  echo {timeout_score} > {container_score_path}; '
            f'  echo Runtime error or invalid execution > {container_output_path}; '
            f'else '
            f'  score=$(echo $output | cut -d \\" \\" -f1); '
            f'  filepath=$(echo $output | cut -d \\" \\" -f2-); '
            f'  echo $score > {container_score_path}; '
            f'  cat \\"$filepath\\" > {container_output_path}; '
            f'fi"'
    )

    elif languages[file_extension]["type"] == "interpreted":
        interpreter = languages[file_extension]["interpreter"]
        command = (
            f'bash -c "cd \\"/app/{problem_name}\\" && '
            f'export JUDGY_SOURCE_FILE={judgy_source_file};'
            f'output=$(timeout 60s python3 judge.py {interpreter} \\"{container_user_file}\\"); '
            f'status=$?; '
            f'if [ $status -eq 124 ]; then '
            f'  echo {timeout_score} > {container_score_path}; '
            f'  echo Your program timed out > {container_output_path}; '
            f'elif [ $status -ne 0 ]; then '
            f'  echo {timeout_score} > {container_score_path}; '
            f'  echo Runtime error > {container_output_path}; '
            f'else '
            f'  score=$(echo $output | cut -d \\" \\" -f1); '
            f'  filepath=$(echo $output | cut -d \\" \\" -f2-); '
            f'  echo $score > {container_score_path}; '
            f'  cat \\"$filepath\\" > {container_output_path}; '
            f'fi"'
        )

    elif languages[file_extension]["type"] == "compiled":
        compiler = languages[file_extension]["compiler"]
        command = (
            f'bash -c "cd \\"/app/{problem_name}\\" && '
            f'{compiler} \\"{container_user_file}\\" -o a.out;'
            f'status=$?; '
            f'if [ $status -ne 0 ]; then '
            f' echo {timeout_score} > {container_score_path}; '
            f' echo Compilation failed > {container_output_path}; '
            f' exit 1; '
            f'fi;'
            f'export JUDGY_SOURCE_FILE={judgy_source_file};'
            f'output=$(timeout 60s python3 judge.py ./a.out);'
            f'status=$?; '
            f'if [ $status -eq 124 ]; then '
            f' echo {timeout_score} > {container_score_path}; '
            f' echo Your program timed out > {container_output_path};'
            f'else'
            f' score=$(echo $output | cut -d \\" \\" -f1); '
            f' filepath=$(echo $output | cut -d \\" \\" -f2-); '
            f' echo $score > {container_score_path}; '
            f' cat \\"$filepath\\" > {container_output_path}; '
            f'fi"'
        )    
    try:
        container = client.containers.run(
            docker_image,
            command=command,
            volumes=volumes,
            detach=True,
        )
        container.wait()  
    finally:
        container.stop()
        container.remove()
            
    return score_file, output_file, language, judgy_source_file
