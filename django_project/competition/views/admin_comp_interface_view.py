from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from competition.models import Competition


@user_passes_test(lambda u: u.is_superuser)
def admin_comp_interface(request, code):
    competition = get_object_or_404(Competition, code=code)
    
    context = {
        'competition': competition,
        'problems': competition.problem_set.all().order_by("number"),
    }


    return render(request, 'judgy/admin_comp_interface.html', context=context)
    
    
