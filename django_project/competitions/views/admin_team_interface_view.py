from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render,get_object_or_404
from competitions.models import Competition, Team

@user_passes_test(lambda u: u.is_superuser)
def admin_team_interface(request, code, name):
    competition = get_object_or_404(Competition, code=code)
    team = get_object_or_404(Team, name=name)

    
    
    context = {
        'competition': competition,
        'team': team
    }


    return render(request, 'judgy/admin_team_interface.html', context=context)