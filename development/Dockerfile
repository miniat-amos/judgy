FROM python:3.12-slim

RUN mkdir -p /app/django_project

WORKDIR /app/django_project

# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 

RUN pip install --upgrade pip

COPY requirements.txt /app/django_project

RUN pip install --no-cache-dir -r requirements.txt
