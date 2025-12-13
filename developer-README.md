# Developer Instructions

## Install the correct Python version to start the project

###  Follow the install steps for your desired OS and shell:

This will install a software called pyenv. An environment to install Python versions safely.

- https://github.com/pyenv/pyenv?tab=readme-ov-file

### Installing the correct version

1. Go to the root of the judgy project directory
2. Install the correct version with pyenv: `pyenv install 3.12`
3. Have this project directory to use this version: `pyenv local 3.12`

### Creating and activating a Python virtual environment

1. We need to create a Python virtual environment to install the project dependencies: `python3 -m venv env`
2. Then we need to activate the virtual environment: `source ./env/bin/activate`

### Installing the dependencies

We need to then install the dependencies into this new virtual environment: `pip3 install -r requirements.txt`

---

### `pipreqs --savepath=requirements.in && pip-compile`

- REQUIRED:
  - `pip3 install pipreqs`
  - `pip3 install pip-tools`
- Creates the requirements.in file which will then apply all dependencies to requirements.txt
- This is for when you install new dependencies in your virtual env while developing

---

## Django Basic Commands

### `python3 manage.py runserver`

- Starts the development server.

---
## Redis and Celery

#### In a seperate terminal, in the parent judgy folder:

### `redis-server`

- Starts the redis server, which celery uses as a message broker.
- Run this before starting the celery worker.

#### In another terminal, in judgy/django_project:

### `celery -A progcomp worker -l info`

- Starts celery worker for progcomp.
- `-l info` logs info for useful runtime output.

---

## Django Database Migrations Commands

### `python3 manage.py makemigrations`

- Generates new database migration files based on model changes.

### `python3 manage.py migrate`

- Applies database migrations to synchronize the database schema.

---

## Docker Commands for running the mySQL container

#### _Prerequisites - Docker and Docker Compose installed on system_

### `sudo docker compose build`

- Uses the .yml file to build the docker image

### `sudo docker compose up -d`

- Starts a container using that image