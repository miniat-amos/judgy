from django.contrib.auth import login
from django.shortcuts import render, redirect
from judgy.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('judgy:see_competitions')
    else:
        form = AuthenticationForm()
    return render(request, 'judgy/login.html', {'form': form})
