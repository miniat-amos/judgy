from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from competition.models import Competition
from competition.utils import calculate_rankings

def rankings_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    rankings = calculate_rankings(competition)
    return JsonResponse(rankings, safe=False)
