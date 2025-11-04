from django.shortcuts import render, redirect

def home_view(request):
    if request.user.is_authenticated:
        return redirect('competitions:see_competitions')
    else:
        return render(
            request, 'judgy/index.html'
        )