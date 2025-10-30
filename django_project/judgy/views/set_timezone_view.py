import json
from django.shortcuts import redirect


def set_timezone_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['django_timezone'] = data.get('timezone')
    return redirect('judgy:home')