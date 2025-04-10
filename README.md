# Instructions and Tools for the developers of the judgy Programming Competition site

---

## Python Virtual Env Commands

#### _Prerequisite - Python Virtual Environment installed on system_

### `python3 -m venv env`

- Creates a Python Virtual Environment

### `source ./env/bin/activate`

- Activates the environment

### `pipreqs --savepath=requirements.in && pip-compile`

- REQUIRED:
  - `pip3 install pipreqs`
  - `pip3 install pip-tools`
- Creates the requirements.in file which will then apply all dependencies to requirements.txt
- This is for when you install new dependencies in your virtual env while developing

### `pip3 install -r requirements.txt`

- Recursively installs all dependencies from requirements.txt

---

## Django Basic Commands

### `python3 manage.py runserver`

- Starts the development server.

---
## Redis and Celery

#### In the parent judgy folder:

### `redis-server`

- Starts the redis server, which celery uses as a message broker.
- Run this before starting the celery worker.

#### In judgy/django_project:

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
