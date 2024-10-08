import logging
import json
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import AuthenticationForm, CustomUserCreationForm, CompetitionCreationForm, UploadFileForm
from .models import Competition
from .functions import start_containers

logger = logging.getLogger(__name__)

def home_view(request):
    return render(request, 'judgy/index.html')

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

@login_required
def submissions(request):
    if request.method == "POST":
        logger.info("POST request received.")
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info("Form is valid.")
            current_user = request.user
            output_file, score_file = start_containers(request.FILES["file"], current_user)
        
            with open(output_file, 'r') as f:
                user_output = f.read()
                
            with open(score_file, 'r') as f:
                user_score = f.read()
                
            context = {'user_output': user_output,
                       'user_score': user_score}
            
            return render(request, "judgy/submissions.html", context)
            
        else:
            logger.error("Form is invalid.")
            logger.error(form.errors)  # Log the errors
            return render(request, 'judgy/submissions.html', {'form': form})
    else:
        logger.info("GET request received.")
        form = UploadFileForm()
    return render(request, "judgy/submissions.html", {"form": form})