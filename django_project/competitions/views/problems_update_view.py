from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, get_object_or_404
from competitions.forms import ProblemForm
from competitions.models import Competition
from competitions.utils import create_problem

@user_passes_test(lambda u: u.is_superuser)
def problems_update_view(request, code):
    competition = get_object_or_404(Competition, code=code)

    if request.method == 'POST':
        problem_form = ProblemForm(request.POST, request.FILES)
        if (problem_form.is_valid()):
            problem = problem_form.save(commit=False)
            problem.competition = competition
            problem.save()

            description = request.FILES.get('description')
            judge_py = request.FILES.get('judge_py')
            other_files = request.FILES.getlist('other_files')

            dist = [
                key[len('distribute['):-1]
                for key, val in request.POST.items()
                if key.startswith('distribute[')
            ]

            create_problem(code, problem.name, description, judge_py, other_files, dist)
     
            return redirect('competitions:competition_code', code=competition.code)
        else:
            print('form.errors:\n', problem_form.errors)
