import os
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from judgy.decorators import verified_required
from judgy.forms import SubmissionForm
from judgy.models import (
    Competition,
    Problem,
    Team,
    Submission
)
from judgy.tasks import process_submission
from judgy.utils import make_temp_dir

@verified_required
def submit_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)
    problem = get_object_or_404(Problem, competition=competition, name=problem_name)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None
    user = request.user

    if request.method == 'POST':
        if competition.start <= timezone.now() < competition.end and user_team:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                files = request.FILES.getlist('files')

                file_paths = []
                save_dir = make_temp_dir(user)
                
                for existing in os.listdir(save_dir):
                    file_path = os.path.join(save_dir, existing)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        
                for f in files:
                    save_path = os.path.join(save_dir, f.name)
                    with open(save_path, 'wb+') as dest:
                        for chunk in f.chunks():
                            dest.write(chunk)
                    file_paths.append(save_path)

                process_submission.delay(code, competition.code, problem.id, problem_name, user_team.id, request.user.id, file_paths)

                latest_submission = Submission.objects.filter(user=user, problem=problem).first()
                
                user_submission = {
                    "problem": problem.name,
                    "score": latest_submission.score
                }
                
                return JsonResponse(user_submission, safe=False)
            else:
                print('Some field was incorrectly filled out.')
                print('form.errors:\n', form.errors)
