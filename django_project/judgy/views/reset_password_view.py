from datetime import timedelta
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from judgy.forms import ResetPasswordForm
from judgy.models import User, UserUniqueToken

def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    token_instance = UserUniqueToken.objects.get(user_id=user, token=token)
    time_generated = token_instance.creation_time
    time_window = 10
        
    if user is not None and time_generated > (timezone.now() - timedelta(minutes=time_window)) :
        if request.method == 'POST':
            form = ResetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('judgy:login')
            else:
                return render(request, 'judgy/reset_password.html', {
                    'form': form,
                })
        else:
            form = ResetPasswordForm(user)
        return render(request, 'judgy/reset_password.html', {'form': form})
    else:
        # Token is invalid or expired (e.g., already used or replaced)
        message = "This password reset link is invalid or has expired. Please request a new one."
        return render(request, 'judgy/reset_password.html', {
            'form': None,
            'invalid_link_message': message,
        })