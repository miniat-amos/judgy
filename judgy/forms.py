from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True

        self.fields['first_name'].widget.attrs.update({
            'id': 'first_name',
            'class': 'form-control',
            'autocomplete': 'given-name',
            'autofocus': False,
            'placeholder': 'First Name'
        })
        self.fields['last_name'].widget.attrs.update({
            'id': 'last_name',
            'class': 'form-control',
            'autocomplete': 'family-name',
            'autofocus': False,
            'placeholder': 'Last Name'
        })
        self.fields['email'].widget.attrs.update({
            'id': 'email',
            'class': 'form-control',
            'autocomplete': 'email',
            'autofocus': False,
            'placeholder': 'Email Address'
        })
        self.fields['password1'].widget.attrs.update({
            'id': 'password1',
            'class': 'form-control',
            'autocomplete': 'new-password',
            'autofocus': False,
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'id': 'password2',
            'class': 'form-control',
            'autocomplete': 'new-password',
            'autofocus': False,
            'placeholder': 'Password Confirmation'
        })

        if 'usable_password' in self.fields:
            del self.fields['usable_password']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)

class AuthenticationForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'id': 'email',
            'class': 'form-control',
            'autocomplete': 'email',
            'autofocus': True,
            'placeholder': 'email'
        })
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'class': 'form-control',
            'autocomplete': 'current-password',
            'placeholder': 'password'
        })
    )

    error_messages = {
        'invalid_login': 'Please enter correct email and password.'
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email is not None and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
        return self.cleaned_data

    def get_user(self):
        return self.user
