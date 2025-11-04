from django.http import JsonResponse
from competitions.models import Competition

def competitions_view(request):
    return JsonResponse(list(Competition.objects.all().values()), safe=False)
