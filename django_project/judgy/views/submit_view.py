import math
from django.db.models import Min, Max
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.utils.html import format_html
from judgy.decorators import verified_required
from judgy.forms import SubmissionForm
from judgy.models import (
    Competition,
    Problem,
    Team,
    Submission,
    User
)

from notifications.models import Notification
from judgy.functions import run_submission

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
                score_file, output_file, language, file_name = run_submission(code, problem, user_team, request.user, files)
                request.session['output_dir'] = str(output_file)
                
                with open(score_file, 'r') as f:
                    score = f.read()
                score = score.split(' ')[0]
                
                with open (output_file, 'r') as f:
                    file_output = f.read()

                if problem.show_output:
                    output_url = f'/competition/{code}/{problem_name}/submission/output'
                    body = format_html(
                        'You got a score of {} in the problem "{}" for the competition "{}".<br>'
                        'Click <a href="{}" target="_blank">here</a> to see the output.',
                        score,
                        problem.name,
                        competition.name,
                        output_url
                    )
                else:
                    body=f'You got a score of {score} in the problem "{problem.name}" for the competition "{competition.name}".'

                Notification.objects.create(
                    user=request.user,
                    header='Your Score',
                    body=body,
                )

                competition_submissions = Submission.objects.filter(problem=problem)
                if problem.score_preference: # Higher Score is Better
                    competition_best_score = competition_submissions.aggregate(Max('score'))['score__max'] or -math.inf
                    if int(score) > competition_best_score:
                        superusers = User.objects.filter(is_superuser=True)
                        participants = User.objects.filter(teams__competition=competition)
                        header = 'New Best Score'
                        body = f'{request.user.first_name} from team "{user_team}" has achieved a new best score of {score} in the problem "{problem.name}" for the competition "{competition.name}"!'
                        for user in superusers:
                            Notification.objects.create(user=user, header=header, body=body)
                        for user in participants:
                            Notification.objects.create(user=user, header=header, body=body)
                else: # Lower Score is Better
                    competition_best_score = competition_submissions.aggregate(Min('score'))['score__min'] or +math.inf
                    if int(score) < competition_best_score:
                        superusers = User.objects.filter(is_superuser=True)
                        participants = User.objects.filter(teams__competition=competition)
                        header = 'New Best Score',
                        body = f'{request.user.first_name} from team "{user_team}" has achieved a new best score of {score} in the problem "{problem.name}" for the competition "{competition.name}"!'
                        for user in superusers:
                            Notification.objects.create(user=user, header=header, body=body)
                        for user in participants:
                            Notification.objects.create(user=user, header=header, body=body)

                Submission.objects.create(problem=problem, team=user_team, user=request.user, language=language, file_name=file_name, output=file_output, score=score)

                return redirect('judgy:competition_code', code=code)
            else:
                print('Some field was incorrectly filled out.')
                print('form.errors:\n', form.errors)
