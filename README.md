# Admin Instructions

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

## Install Docker on your host system

Install Docker for your desired OS. Docker is mainly intended for Linux, if you are using Docker on Mac or Windows you need to install Docker Desktop instead.

Linux - https://docs.docker.com/engine/install/

Others - https://docs.docker.com/desktop/

I will be using Linux CLI commands for this setup.

## Add your user to the Docker group 

If it doesn't exist: `sudo groupadd docker`

Add yourself: `sudo usermod -aG docker $USER`

To automatically see your user in this group run this: `newgrp docker`

---

## Create a .env file

Create the file: `touch .env`

Here is our .env-example:

```
# MySQL settings
MYSQL_BACKEND="django.db.backends.mysql"
MYSQL_HOST="localhost"
MYSQL_PORT="FILL_IN_YOUR_PORT"
MYSQL_DATABASE="FILL_IN_YOUR_DATABASE"
MYSQL_USER="FILL_IN_YOUR_USER"
MYSQL_PASSWORD="FILL_IN_YOUR_PASSWORD"
MYSQL_ROOT_PASSWORD="FILL_IN_YOUR_ROOT_PASSWORD"

# Email Settings
EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_USE_TLS="True"
EMAIL_HOST_USER="FILL_IN_YOUR_HOST_USER"
EMAIL_HOST_PASSWORD="FILL_IN_YOUR_HOST_PASSWORD"

# Nginx/Django Settings
SUPER_USER_EMAIL="FILL_IN_YOUR_EMAIL"
SUPER_USER_FIRST_NAME="FILL_IN_YOUR_FIRST_NAME"
SUPER_USER_LAST_NAME="FILL_IN_YOUR_LAST_NAME"

SERVER_PORT="FILL_IN_YOUR_PORT"
SERVER_NAME="FILL_IN_DOMAIN_NAME"
ALLOWED_HOSTS="FILL_IN_DOMAIN_NAME"
KEY="FILL_IN_SERVER_KEY"
DEBUG=False
```

This env file holds credentials for the MySQL DB, Email auth and misc. Django settings.

### MySQL env settings

- MySQL is ran in a Docker container, so leave the MYSQL_HOST as localhost.
- The default port for MySQL is usually 3306, but if you are using that port, then make it any free port to your desire (>1024).

### Super user settings

- The super user is the admin account for the programming competition website.
- This admin account will be created when you run the script in the next steps. It will ask for the password when you run this script.

### Django settings

#### Server Vars

- The SERVER_NAME is for Nginx and the ALLOWED_HOSTS is for Django.
- These need to be the domain name of your server (ex. judgy.cs.sunypoly.edu).
- The SERVER_PORT is the port where Django will be running from, the default is 8000, but make it any free port of your desire (>1024).

#### Key

- This is the Django secret key that is used for cryptographic uses.
- The easiest way to get a key is by creating one from this website and pasting it in the .env file: https://djecrety.ir/

#### Debug

- **LEAVE THIS AS IS, IT NEEDS TO STAY FALSE AND OUT OF QUOTES**

## Starting up the Web Server

We have created a nice script that starts up Django, MySQL, and Nginx.

### Prerequisites

#### Server Certificate and Key

1. Create a certs directory in the root of the judgy project directory: `mkdir certs`
2. Name your certficiate: `judgy.crt`
3. Name your key: `judgy.pem`
4. Store these inside of the new `certs` directory

#### Install redis server and start it

- Example using apt: `sudo apt install redis-server`
- Starting redis: `sudo systemctl enable --now redis`

#### Add these export variables into your .bashrc

- export XDG_RUNTIME_DIR="/run/user/$(id -u)"
- export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"

### Run the entrypoint.sh

**Make sure the user you are doing this setup on has sudo privileges**

- `chmod +x entrypoint.sh`

- `./entrypoint.sh`

#### This script will do multiple things:

##### Start Uvicorn and Celery:

1. It will start Uvicorn (Django web app) on the SERVER_PORT you specified on your host system.
2. It will start Celery on your host system.
3. These both will start as user systemd services.

##### Start MySQL in a container
##### Start Nginx in a container

## Create a super user

- Create a super user running this command: `python3 django_project/make_superuser.py`
- This will ask for a password as input
