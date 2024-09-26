import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class User(AbstractUser):
    '''
    User model where email is the unique identifier for authentication instead of username.
    '''
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class Competition(models.Model):
    code = models.CharField(editable=False, max_length=4, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    enroll_start = models.DateTimeField()
    enroll_end = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                code = uuid.uuid4().hex[:4].upper()
                if not Competition.objects.filter(code=code).exists():
                    self.code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
