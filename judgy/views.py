from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .forms import AuthenticationForm, CustomUserCreationForm, CompetitionCreationForm

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

@login_required
@user_passes_test(lambda u: u.is_superuser)
def competition_create_view(request):
    if request.method == 'POST':
        form = CompetitionCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('judgy:home')
    else:
        form = CompetitionCreationForm()
    return render(request, 'judgy/competition_create.html', { 'form': form })
