from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, get_object_or_404
from competition.forms import ProblemForm
from competition.models import Competition
from competition.utils import create_problem_dir

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
            judging_program = request.FILES.get('judge_py')
            other_files = request.FILES.getlist('other_files')

            dist_files = [
                key[len('distribute['):-1]
                for key, val in request.POST.items()
                if key.startswith('distribute[')
            ]
            
            all_files = []

            if description:
                all_files.append(description)

            if judging_program:
                all_files.append(judging_program)

            all_files.extend(other_files)

            selected_dist_files = [
                file for file in all_files
                if file.name in dist_files
            ]

            create_problem_dir(code, problem.name, description, judging_program, other_files, selected_dist_files)
     
            return redirect('competition:competition_code', code=competition.code)
        else:
            print('form.errors:\n', problem_form.errors)
