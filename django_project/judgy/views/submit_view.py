import math
import os
from django.conf import settings
from django.db.models import Min, Max
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from ..decorators import verified_required
from ..forms import SubmissionForm
from ..models import (
    Competition,
    Problem,
    Team,
    Submission,
    Notification,
    User
)
from ..functions import run_submission
from ..tasks import process_submission

@verified_required
def submit_view(request, code, problem_name):
    competition = get_object_or_404(Competition, code=code)
    problem = get_object_or_404(Problem, competition=competition, name=problem_name)
    user_team = Team.objects.filter(competition=competition, members=request.user).first() if request.user.is_authenticated else None

    if request.method == 'POST':
        if competition.start <= timezone.now() < competition.end and user_team:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                files = request.FILES.getlist('files')

                file_paths = []
                save_dir = os.path.join(settings.MEDIA_ROOT, 'temp_submissions')
                os.makedirs(save_dir, exist_ok=True)
                for f in files:
                    save_path = os.path.join(save_dir, f.name)
                    with open(save_path, 'wb+') as dest:
                        for chunk in f.chunks():
                            dest.write(chunk)
                    file_paths.append(save_path)

                print(type(file_paths), file_paths)

                process_submission.delay(code, competition.code, problem.id, problem_name, user_team.id, request.user.id, file_paths)

                return redirect('judgy:competition_code', code=code)
            else:
                print('Some field was incorrectly filled out.')
                print('form.errors:\n', form.errors)
