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

## Django Database Migrations Commands

### `python3 manage.py makemigrations`

- Use this after you make changes to your models. This creates migrations files which are human readable formats of the changes you are making.

### `python3 manage.py migrate`

- Use this after running makemigrations to actually apply the changes

---

## Docker Commands for running the mySQL container

#### _Prerequisites - Docker and Docker Compose installed on system_

### `sudo docker compose build`

- Uses the .yml file to build the docker image

### `sudo docker compose up -d`

- Starts a container using that image
