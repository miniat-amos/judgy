from django.shortcuts import render
from ..models import (Competition)
from ..forms import CompetitionCreationForm
from django.utils import timezone
def see_competitions_view(request):
    now = timezone.now()

    past_competitions = Competition.objects.filter(end__lte=now).order_by('-end')
    ongoing_competitions = Competition.objects.filter(
        start__lte=now, end__gt=now
    ).order_by('end')
    
    upcoming_competitions = Competition.objects.filter(start__gt=now).order_by('start')
    
    update_comp_form = CompetitionCreationForm()

    return render(
        request,
        'judgy/view_competitions.html',
        {
            'past_competitions': past_competitions,
            'ongoing_competitions': ongoing_competitions,
            'upcoming_competitions': upcoming_competitions,
            'update_comp_form': update_comp_form,

        },
    )