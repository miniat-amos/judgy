from judgy.forms import AccountVerificationForm
from django.shortcuts import render, redirect
from django.urls import reverse
from judgy.tasks import send_6dc_email_task


def verify_view(request):
    if request.method == 'POST':
        form = AccountVerificationForm(data=request.POST)
        form.user = request.user
        if form.is_valid():
            request.user.is_verified = True
            request.user.save()
            return redirect(reverse('judgy:register') + '?step=3')  

        else:
            print('6-digit code provided is incorrect')
            print('form.errors:\n', form.errors)
    else:
        form = AccountVerificationForm()
        send_6dc_email_task.delay(request.user.id, request.user.email)

    return render(request, 'judgy/verify.html', {'form': form})