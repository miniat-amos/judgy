from django.db import models
from judgy.models import User
from competitions.models import Team

# Create your models here.
class Notification(models.Model):
    type = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    header = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.header

class TeamJoinNotification(Notification):
    request_user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.type = 1
        self.header = 'Join Request'
        TeamJoinNotification.objects.filter(
            user=self.user,
            request_user=self.request_user,
            team=self.team
        ).delete()
        super().save(*args, **kwargs)

class TeamInviteNotification(Notification):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.type = 1
        self.header = 'Team Invite'
        TeamInviteNotification.objects.filter(
            user=self.user,
            team=self.team
        ).delete()
        super().save(*args, **kwargs)