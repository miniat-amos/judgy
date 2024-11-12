import random
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = ''.join(random.choices('0123456789', k=6))
        super().save(*args, **kwargs)

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
    color = models.CharField(max_length=7)

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

class Team(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    members = models.ManyToManyField('User', related_name='teams')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'name'], name='unique_competition_team_name')
        ]

    def __str__(self):
        return self.name
