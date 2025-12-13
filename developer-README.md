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

**You need to activate this virtual environment everytime you go to work on the project.**

### Installing the dependencies

We need to then install the dependencies into this new virtual environment: `pip3 install -r requirements.txt`

---

## Development Commands

### Start the dev environment

#### Prerequisites

##### Staticfiles
We use uvicorn to start the dev server and it does not handle static files by default.

`cd django_project && python3 manage.py collectstatic`

##### Install redis server and start it

- Example using apt: `sudo apt install redis-server`
- Starting redis: `sudo systemctl enable --now redis`

#### Start Uvicorn

In a terminal inside of `judgy/django_project` start uvicorn.

The command to start the webserver on localhost is:

`uvicorn progcomp.asgi:application --reload --reload-include '*.html' --port 8000`

Then go to localhost:8000 on your browser, if your port 8000 is being used, then change it to any other port (1024>).

#### Start Celery

In another terminal inside of `judgy/django_project` start celery.

- `celery -A progcomp worker -l info`



## Django Database Migrations Commands

### `python3 manage.py makemigrations`

- Generates new database migration files based on model changes.

### `python3 manage.py migrate`

- Applies database migrations to synchronize the database schema.

---

## Docker Commands for running the MySQL container

#### _Prerequisites - Docker and Docker Compose installed on system_

### `sudo docker compose build`

- Uses the .yml file to build the docker image

### `sudo docker compose up -d`

- Starts a container using that image