from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from judgy.models import Competition, Team

def get_members_view(request, code, name):
    competition = get_object_or_404(Competition, code=code)
    team = get_object_or_404(Team, competition=competition, name=name)
    
    return JsonResponse(list(team.members.all().values('email', 'first_name')), safe=False)