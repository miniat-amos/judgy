import os
from django.core.wsgi import get_wsgi_application

# Set the settings module to settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'progcomp.settings')

# Initialize Django
application = get_wsgi_application()

from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()

# Create a superuser
if not User.objects.filter(email=config('SUPER_USER_EMAIL')).exists():
    User.objects.create_superuser(
        email=config('SUPER_USER_EMAIL'),
        password=input('Input super user password: '),
        first_name=config('SUPER_USER_FIRST_NAME'),
        last_name=config('SUPER_USER_LAST_NAME')
    )
