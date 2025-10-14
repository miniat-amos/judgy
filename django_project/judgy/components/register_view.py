from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.utils import timezone
from ..forms import CustomUserCreationForm
from ..models import Competition
from ..tasks import send_6dc_email_task

def register_view(request):
    now = timezone.now()
    enrollable_competitions = Competition.objects.filter(enroll_start__lte=now, enroll_end__gt=now).order_by('enroll_end')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_6dc_email_task.delay(user.id, user.email)
            return redirect('judgy:verify')
        else:
            print('Any field in the registration form was not filled out right.')
            print('form.errors:\n', form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request, 'judgy/register.html', {'form': form, 'enrollable_comps': enrollable_competitions})
