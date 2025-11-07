import os
import django
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "progcomp.settings")
django.setup()

from django.shortcuts import redirect, get_object_or_404
from judgy.models import User, Team, Competition
from notifications.models import Notification

code = "d515"

competition = get_object_or_404(Competition, code=code)

participants = User.objects.filter(teams__competition=competition)

super_user = User.objects.filter(is_superuser=True)

header = "sssd"

body = "hello"

for user in participants:
    Notification.objects.create(user=user, header=header, body=body)

for user in super_user:
    Notification.objects.create(user=user, header=header, body=body)
