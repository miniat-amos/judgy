import uuid
from django.db import models
from judgy.models import User

# Create your models here.
class Competition(models.Model):
    code = models.CharField(editable=False, max_length=4, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    enroll_start = models.DateTimeField()
    enroll_end = models.DateTimeField()
    team_size_limit = models.PositiveIntegerField(default=4)
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
    
class Problem(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    score_preference = models.BooleanField(default=True)
    show_output = models.BooleanField(default=True)
    subjective = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'number'], name='unique_competition_problem_number'),
            models.UniqueConstraint(fields=['competition', 'name'], name='unique_competition_problem_name')
        ]

    def __str__(self):
        return self.name
    

class Team(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='teams')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'name'], name='unique_competition_team_name')
        ]

    def __str__(self):
        return self.name
    

class Submission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=50, default="")
    file_name = models.CharField(max_length=50, default="")
    output = models.TextField(blank=True, null=True)
    score = models.BigIntegerField(blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)