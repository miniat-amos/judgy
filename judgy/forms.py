from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils import timezone
from .models import User, Competition


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
        self.fields["password1"].required = True
        self.fields["password2"].required = True

        self.fields["first_name"].widget.attrs.update(
            {
                "id": "first_name",
                "class": "form-control",
                "autocomplete": "given-name",
                "autofocus": False,
                "placeholder": "First Name",
            }
        )
        self.fields["last_name"].widget.attrs.update(
            {
                "id": "last_name",
                "class": "form-control",
                "autocomplete": "family-name",
                "autofocus": False,
                "placeholder": "Last Name",
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "id": "email",
                "class": "form-control",
                "autocomplete": "email",
                "autofocus": False,
                "placeholder": "Email Address",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "id": "password1",
                "class": "form-control",
                "autocomplete": "new-password",
                "autofocus": False,
                "placeholder": "Password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "id": "password2",
                "class": "form-control",
                "autocomplete": "new-password",
                "autofocus": False,
                "placeholder": "Password Confirmation",
            }
        )

        if "usable_password" in self.fields:
            del self.fields["usable_password"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email",)


class AuthenticationForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "id": "email",
                "class": "form-control",
                "autocomplete": "email",
                "autofocus": True,
                "placeholder": "Email Address",
            }
        ),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "id": "password",
                "class": "form-control",
                "autocomplete": "current-password",
                "autofocus": False,
                "placeholder": "Password",
            }
        ),
    )

    error_messages = {"invalid_login": "Please enter correct email and password."}

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email is not None and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
        return self.cleaned_data

    def get_user(self):
        return self.user


class CompetitionCreationForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = [
            "name",
            "description",
            "start",
            "end",
            "enroll_start",
            "enroll_end",
            "color",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["name"].required = True
        self.fields["description"].required = True
        self.fields["start"].required = True
        self.fields["end"].required = True
        self.fields["enroll_start"].required = True
        self.fields["enroll_end"].required = True
        self.fields["color"].required = True

        self.fields["name"].widget.attrs.update(
            {
                "id": "name",
                "class": "form-control",
                "autofocus": True,
                "placeholder": "Competition Name",
            }
        )
        self.fields["description"].widget.attrs.update(
            {
                "id": "description",
                "class": "form-control",
                "autofocus": False,
                "placeholder": "Competition Description",
            }
        )
        self.fields["start"].widget.attrs.update(
            {
                "id": "start",
                "class": "form-control",
                "autofocus": False,
                "type": "datetime-local",
            }
        )
        self.fields["end"].widget.attrs.update(
            {
                "id": "end",
                "class": "form-control",
                "autofocus": False,
                "type": "datetime-local",
            }
        )
        self.fields["enroll_start"].widget.attrs.update(
            {
                "id": "enroll-start",
                "class": "form-control",
                "autofocus": False,
                "type": "datetime-local",
            }
        )
        self.fields["enroll_end"].widget.attrs.update(
            {
                "id": "enroll-end",
                "class": "form-control",
                "autofocus": False,
                "type": "datetime-local",
            }
        )
        self.fields["color"].widget.attrs.update(
            {
                "id": "color",
                "class": "form-control",
                "autofocus": False,
                "type": "color",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        enroll_start = cleaned_data.get("enroll_start")
        enroll_end = cleaned_data.get("enroll_end")

        # Validate that start is before end
        if start and end and start >= end:
            self.add_error("end", "End date must be after start date.")

        # Validate that enroll_start is before enroll_end
        if enroll_start and enroll_end and enroll_start >= enroll_end:
            self.add_error(
                "enroll_end", "Enrollment end date must be after enrollment start date."
            )

        # Validate that the dates are not in the past
        now = timezone.now()
        if start and start < now:
            self.add_error("start", "Start date cannot be in the past.")
        if end and end < now:
            self.add_error("end", "End date cannot be in the past.")
        if enroll_start and enroll_start < now:
            self.add_error(
                "enroll_start", "Enrollment start date cannot be in the past."
            )
        if enroll_end and enroll_end < now:
            self.add_error("enroll_end", "Enrollment end date cannot be in the past.")

        return cleaned_data


class UploadFileForm(forms.Form):
    file = forms.FileField()


class ProblemCreationForm(forms.Form):
    name = forms.CharField(
        label="Problem Name",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Problem Name",
                "autofocus": True,
            }
        ),
    )
    zip = forms.FileField(
        label="Problem Zip",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".zip",
            }
        ),
    )
    input_files = forms.FileField(
        label="Problem Test File(s)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )
    judging_program = forms.FileField(
        label="Judging Program",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".py, .cpp, .java",
            }
        ),
    )
