import random
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from judgy.managers import UserManager

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
    
class UserUniqueToken(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    creation_time = models.DateTimeField(default=timezone.now)





