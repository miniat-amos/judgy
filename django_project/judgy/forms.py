from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from judgy.models import User

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

        self.fields['first_name'].widget.attrs.update(
            {
                'id': 'first_name',
                'class': 'form-control',
                'autocomplete': 'given-name',
                'autofocus': False,
                'placeholder': 'First Name',
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'id': 'last_name',
                'class': 'form-control',
                'autocomplete': 'family-name',
                'autofocus': False,
                'placeholder': 'Last Name',
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'id': 'email',
                'class': 'form-control',
                'autocomplete': 'email',
                'autofocus': False,
                'placeholder': 'Email Address',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'id': 'password1',
                'class': 'form-control',
                'autocomplete': 'new-password',
                'autofocus': False,
                'placeholder': 'Password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'id': 'password2',
                'class': 'form-control',
                'autocomplete': 'new-password',
                'autofocus': False,
                'placeholder': 'Password Confirmation',
            }
        )

        if 'usable_password' in self.fields:
            del self.fields['usable_password']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)

class AuthenticationForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'id': 'email',
                'class': 'form-control',
                'autocomplete': 'email',
                'autofocus': True,
                'placeholder': 'Email Address',
            }
        ),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'id': 'password',
                'class': 'form-control',
                'autocomplete': 'current-password',
                'autofocus': False,
                'placeholder': 'Password',
            }
        ),
    )

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
                raise forms.ValidationError('Invalid login. Please enter the correct email and password.')
        return self.cleaned_data

    def get_user(self):
        return self.user

class AccountVerificationForm(forms.Form):
    code1 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'id': 'code1',
        'class': 'code form-control text-center',
        'autofocus': True
    }))
    code2 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'id': 'code2',
        'class': 'code form-control text-center',
        'autofocus': False
    }))
    code3 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'id': 'code3',
        'class': 'code form-control text-center',
        'autofocus': False
    }))
    code4 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'id': 'code4',
        'class': 'code form-control text-center',
        'autofocus': False
    }))
    code5 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'id': 'code5',
        'class': 'code form-control text-center',
        'autofocus': False
    }))
    code6 = forms.CharField(max_length=1, widget=forms.TextInput(attrs={
        'id': 'code6',
        'class': 'code form-control text-center',
        'autofocus': False
    }))

    def clean(self):
        cleaned_data = super().clean()
        code = ''.join([
            cleaned_data.get('code1'),
            cleaned_data.get('code2'),
            cleaned_data.get('code3'),
            cleaned_data.get('code4'),
            cleaned_data.get('code5'),
            cleaned_data.get('code6')
        ])
        if not code:
            raise forms.ValidationError('Please enter the six-digit verification code.')
        if not code == self.user.verification_code:
            raise forms.ValidationError('Invalid code. Please enter the correct six-digit verification code.')
        return cleaned_data

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email Address"
        })
    )

class ResetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new password",
            "id": "id_new_password1"
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm new password",
            "id": "id_new_password2"
        }),
        strip=False,
    )





