import json
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import AuthenticationForm, CustomUserCreationForm, CompetitionCreationForm
from .models import Competition

def home_view(request):
    now = timezone.now()

    past_competitions = Competition.objects.filter(end__lt=now).order_by('-end')
    ongoing_competitions = Competition.objects.filter(start__lte=now, end__gte=now).order_by('end')
    upcoming_competitions = Competition.objects.filter(start__gt=now).order_by('start')

    return render(request, 'judgy/index.html', {
        'past_competitions': past_competitions,
        'ongoing_competitions': ongoing_competitions,
        'upcoming_competitions': upcoming_competitions
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('judgy:home')
    else:
        form = AuthenticationForm()
    return render(request, 'judgy/login.html', { 'form': form })

def logout_view(request):
    logout(request)
    return redirect('judgy:home')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect('judgy:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'judgy/register.html', { 'form': form })

def set_timezone_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['django_timezone'] = data.get('timezone')
    return redirect('judgy:home')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def competition_create_view(request):
    if request.method == 'POST':
        form = CompetitionCreationForm(data=request.POST)
        if form.is_valid():
            competition = form.save()
            return redirect('judgy:competition_code', code=competition.code)
    else:
        form = CompetitionCreationForm()
    return render(request, 'judgy/competition_create.html', { 'form': form })

def competition_code_view(request, code):
    competition = get_object_or_404(Competition, code=code)
    return render(request, 'judgy/competition_code.html', { 'competition': competition })
