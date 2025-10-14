from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import Competition, Team

def get_teams_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    teams = Team.objects.filter(competition=competition).values()
    
    return JsonResponse(list(teams), safe=False)
