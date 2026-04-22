import os
import tempfile
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from judgy.decorators import verified_required
from competition.forms import SubmissionForm
from competition.models import (
    Competition,
    Problem,
    Team,
    Submission
)
from competition.tasks import celery_process_submission
from competition.utils import create_user_dirs, store_user_submission

@verified_required
def submit_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)
    problem = get_object_or_404(Problem, competition=competition, name=problem_name)
    user = request.user
    team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None

    if request.method == 'POST':
        if competition.start <= timezone.now() < competition.end and team:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                user_files = request.FILES.getlist('files')
                
                submission = Submission.objects.create(
                    problem=problem,
                    team=team,
                    user=user,
                    language="",
                    file_name="",
                    output=None,
                    score=None
                )
                
                user_directories = create_user_dirs(code, user, problem_name, team, submission)
                user_submission = store_user_submission(user_files, user_directories["submission_dir"], user, problem_name, code)

                celery_process_submission.delay(
                    code, 
                    problem.id, 
                    team.id, 
                    user.id,
                    submission.id,
                    user_directories,
                    user_submission
                )
                                    
                return JsonResponse({})
            else:
                print('Some field was incorrectly filled out.')
                print('form.errors:\n', form.errors)
