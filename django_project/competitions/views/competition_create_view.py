from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from competitions.forms import CompetitionCreationForm
from judgy.utils import create_comp_dir

@user_passes_test(lambda u: u.is_superuser)
def competition_create_view(request):
    if request.method == 'POST':
        form = CompetitionCreationForm(data=request.POST)
        if form.is_valid():
            competition = form.save()
            create_comp_dir(str(competition.code))
            return redirect('competitions:competition_code', code=competition.code)
        else:
            print('Any field filled out is invalid.')
            print('form.errors:\n', form.errors)
    else:
        form = CompetitionCreationForm()
    return render(request, 'judgy/competition_create.html', {'form': form})
