import docker
import os
from functools import lru_cache
from pathlib import Path

@lru_cache
def get_mount_map():
    try:
        client = docker.from_env()
        hostname = os.environ.get("HOSTNAME")
        container = client.containers.get(hostname)

        labels = container.attrs["Config"]["Labels"]
        if labels.get("com.docker.compose.service") != "celery":
            return {}

        mount_map = {}
        for mount in container.attrs["Mounts"]:
            if mount["Type"] == "bind":
                mount_map[Path(mount["Destination"])] = Path(mount["Source"])

        return mount_map

    except Exception as e:
        print(f"Mount map error: {e}")
        return {}

def to_host_path(container_path: Path) -> Path:
    for container_root, host_root in get_mount_map().items():
        try:
            return host_root / container_path.relative_to(container_root)
        except ValueError:
            continue
    raise ValueError(f"No host mount found for {container_path}")

def create_container_volumes(host_filepaths):
    container_main_directory = Path("/app")
    
    container_output_dir = container_main_directory / "output"
      
    container_submission_dir = container_main_directory / "submission"
    
    container_tmp_judging = container_main_directory / "judging"
    
    container_tmp_others = container_main_directory / "others"
    
    
    # Volumes for file-to-file binding
    volumes = {
        str(to_host_path(host_filepaths["output_dir"])): {"bind": str(container_output_dir), "mode": "rw"},
        str(to_host_path(host_filepaths["judging_program"])): {"bind": str(container_tmp_judging)},
        str(to_host_path(host_filepaths["other_files"])): {"bind": str(container_tmp_others)},
        str(to_host_path(host_filepaths["user_submission"])): {"bind": str(container_submission_dir)}
    }
    
    return volumes
    