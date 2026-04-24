import docker
from django.conf import settings
from pathlib import Path


def build_judgy_images(code=False):
    
    container_build_path = Path(__file__).resolve().parent

    services = [
        {"name": "python", "base_image": "python:latest"},
        {"name": "gcc", "base_image": "gcc:latest"},
        {"name": "ruby", "base_image": "ruby:latest"},
        {"name": "node", "base_image": "node:latest"},
        {"name": "java", "base_image": "eclipse-temurin:21-jdk"},
    ]
    

    docker_client = docker.from_env()
    
    for service in services:
        tag = f"judgy-{service['name']}"

        print(f"Building {tag}...")

        image, logs = docker_client.images.build(
            path=str(container_build_path),
            dockerfile="Dockerfile",
            tag=tag,
            buildargs={
                "BASE_IMAGE": service["base_image"],
            },
            rm=True,
        )


    print("All images built.")