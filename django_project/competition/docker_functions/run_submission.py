import docker
from pathlib import Path
from competition.utils import make_file, get_problem_dir, create_formatted_name
from .utils import create_container_volumes

languages = {
    ".py": {
            "image": "python", 
            "type": "interpreted", 
            "run_cmd": lambda user_submission: f"python3 {user_submission}", 
            "language": "Python",
        },
    
    ".js": {
            "image": "node", 
            "type": "interpreted", 
            "run_cmd": lambda user_submission: f"node {user_submission}", 
            "language": "JavaScript"
        },
    
    ".rb": {
            "image": "ruby", 
            "type": "interpreted", 
            "run_cmd": lambda user_submission: f"ruby {user_submission}",  
            "language": "Ruby"
        },
    
    ".c": {
            "image": "gcc", 
            "type": "compiled", 
            "compile_cmd": lambda user_submission: f"gcc {user_submission} -o a.out",
            "run_cmd": lambda user_submission: "./a.out", 
            "language": "C"
        },
    
    ".cpp": {
            "image": "gcc", 
            "type": "compiled", 
            "compile_cmd": lambda user_submission: f"g++ {user_submission} -o a.out",
            "run_cmd": lambda user_submission: "./a.out", 
            "language": "C++"
        },
    
    ".java": {
        "image": "java", 
        "type": "compiled-and-interpreted", 
        "compile_cmd": lambda user_submission: f"mv {user_submission} Main.java && javac Main.java", 
        "run_cmd": lambda user_submission: f"java Main", 
        "language": "Java"
        }
}


def run_submission(code, user, problem, user_submission, user_directories):
    

    # TODO: Have failed programs actually fail and not return huge score to user 
    # if problem.score_preference:
    #     timeout_score = -9223372036854775808
    # else:
    #     timeout_score = 9223372036854775808

      
    submitted_files = [Path(f) for f in user_submission]
    submission_dir = Path(user_directories["submission_dir"])
    output_dir = Path(user_directories["output_dir"])
    
    # Variables for local machine
    # Get file extension
    file_extension = submitted_files[0].suffix
    language = languages[file_extension]
    
    language_image = language["image"]
    
    problem_name = problem.name
    
    problem_dir = get_problem_dir(code, problem_name)
    judging_program = problem_dir / "judging_program"
    other_files = problem_dir / "other_files"
    
    score_file = make_file(output_dir, "score.txt")
    output_file = make_file(output_dir, "output.txt")
    
    
    judgy_source_file = submitted_files[0]
   
    host_filepaths = {
        "output_dir": output_dir,
        "judging_program": judging_program,
        "other_files": other_files,
        "user_submission": submission_dir
    }
    
    
    docker_client = docker.from_env()
    
    container_image = f"judgy-{language_image}"
    
    email = user.email.split('@')[0]
    formatted_name = [email, problem_name.replace(" ", "-"), code.lower()]
        
    container_name = create_formatted_name(formatted_name, "-")
    
    container_user_submission = judgy_source_file.name
        
    container_compile_cmd = language.get("compile_cmd")
    if callable(container_compile_cmd):
        container_compile_cmd = container_compile_cmd(container_user_submission)
    else:
        container_compile_cmd = ""
        
    container_run_cmd = language["run_cmd"](container_user_submission)
    
    
    container_command=[
        "/app/judge.sh",
        problem_name,
        container_compile_cmd,
        container_run_cmd,
        container_user_submission
    ]
    
    container_volumes = create_container_volumes(host_filepaths)
    

    container = None
    try:
        container = docker_client.containers.run(
            image=container_image,
            name=container_name,
            command=container_command,
            volumes=container_volumes,
            detach=True,
        )
        container.wait()  
    finally:
        if container is not None:
            container.stop()
            # container.remove()


    return score_file, output_file, language["language"], judgy_source_file.name
