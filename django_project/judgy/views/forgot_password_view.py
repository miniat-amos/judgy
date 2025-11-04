from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from judgy.forms import ForgotPasswordForm
from judgy.models import User, UserUniqueToken

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(data=request.POST)
        if form.is_valid(): 
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                UserUniqueToken.objects.create(user_id=user, token=token)
                reset_password_link = request.build_absolute_uri(
                    reverse('judgy:reset_password', kwargs={'uidb64': uid, 'token': token})
                )
                context = {'reset_link': reset_password_link}
                send_mail(
                    'judgy Password Reset',
                    '',
                    settings.EMAIL_HOST_USER,
                    [email],
                    html_message=render_to_string('judgy/emails/password_reset.html', context)
                )
                return redirect('judgy:home')
            except User.DoesNotExist:
                form.add_error('email', 'No account found with that email address.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'judgy/forgot_password.html', {'form': form})
