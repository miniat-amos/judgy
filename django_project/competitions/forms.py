from django.utils.html import strip_tags
from django import forms
from django.utils import timezone
from competitions.models import Competition, Problem, Submission, Team

class CompetitionCreationForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = [
            'name',
            'description',
            'start',
            'end',
            'enroll_start',
            'enroll_end',
            'team_size_limit',
            'color',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['start'].required = True
        self.fields['end'].required = True
        self.fields['enroll_start'].required = True
        self.fields['enroll_end'].required = True
        self.fields['team_size_limit'].required = True
        self.fields['color'].required = True

        self.fields['name'].widget.attrs.update(
            {
                'id': 'name',
                'class': 'form-control',
                'autofocus': True,
                'placeholder': 'Competition Name',
            }
        )
        self.fields['description'].widget.attrs.update(
            {
                'id': 'description',
                'class': 'form-control',
                'autofocus': False,
                'placeholder': 'Competition Description',
            }
        )
        self.fields['start'].widget.attrs.update(
            {
                'id': 'start',
                'class': 'form-control',
                'autofocus': False,
                'type': 'datetime-local',
            }
        )
        self.fields['end'].widget.attrs.update(
            {
                'id': 'end',
                'class': 'form-control',
                'autofocus': False,
                'type': 'datetime-local',
            }
        )
        self.fields['enroll_start'].widget.attrs.update(
            {
                'id': 'enroll-start',
                'class': 'form-control',
                'autofocus': False,
                'type': 'datetime-local',
            }
        )
        self.fields['enroll_end'].widget.attrs.update(
            {
                'id': 'enroll-end',
                'class': 'form-control',
                'autofocus': False,
                'type': 'datetime-local',
            }
        )
        self.fields['team_size_limit'].widget.attrs.update(
            {
                'id': 'team-size-limit',
                'class': 'form-control',
                'autofocus': False,
                'placeholder': 'Team Size Limit',
            }
        )
        self.fields['color'].widget.attrs.update(
            {
                'id': 'color',
                'class': 'form-control',
                'autofocus': False,
                'type': 'color',
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        enroll_start = cleaned_data.get('enroll_start')
        enroll_end = cleaned_data.get('enroll_end')

        # Validate that start is before end
        if start and end and start >= end:
            self.add_error('end', 'End date must be after start date.')

        # Validate that enroll_start is before enroll_end
        if enroll_start and enroll_end and enroll_start >= enroll_end:
            self.add_error(
                'enroll_end', 'Enrollment end date must be after enrollment start date.'
            )

        # Validate that the dates are not in the past
        now = timezone.now()
        if start and start < now:
            self.add_error('start', 'Start date cannot be in the past.')
        if end and end < now:
            self.add_error('end', 'End date cannot be in the past.')
        if enroll_start and enroll_start < now:
            self.add_error(
                'enroll_start', 'Enrollment start date cannot be in the past.'
            )
        if enroll_end and enroll_end < now:
            self.add_error('enroll_end', 'Enrollment end date cannot be in the past.')

        return cleaned_data

class ProblemForm(forms.ModelForm):
    description = forms.FileField()
    judge_py = forms.FileField()
    other_files = forms.FileField()
    score_preference = forms.ChoiceField(
        choices=[
            (True, 'Higher Score is Better'),
            (False, 'Lower Score is Better')
        ]
    )
    show_output = forms.ChoiceField(
        choices=[
            (True, 'Yes'),
            (False, 'No')
        ]
    )
    
    subjective = forms.ChoiceField(
        choices=[
            (False, 'No'),
            (True, 'Yes')
        ]
    )


    class Meta:
        model = Problem
        fields = [
            'number',
            'name',
            'score_preference',
            'show_output',
            'subjective'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['number'].required = True
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['judge_py'].required = False
        self.fields['other_files'].required = False
        self.fields['score_preference'].required = True
        self.fields['show_output'].required = True
        self.fields['subjective'].required = True


        self.fields['number'].widget.attrs.update(
            {
                'id': 'number',
                'class': 'form-control',
                'placeholder': 'Problem Number'
            }
        )
        self.fields['name'].widget.attrs.update(
            {
                'id': 'name',
                'class': 'form-control',
                'placeholder': 'Problem Name'
            }
        )
        self.fields['description'].widget.attrs.update(
            {
                'id': 'description',
                'class': 'form-control',
                'multiple': False
            }
        )
        self.fields['judge_py'].widget.attrs.update(
            {
                'id': 'judge-py',
                'class': 'form-control',
                'multiple': False
            }
        )
        self.fields['other_files'].widget.attrs.update(
            {
                'id': 'other-files',
                'class': 'form-control',
                'multiple': True
            }
        )
        self.fields['score_preference'].widget.attrs.update(
            {
                'id': 'score-preference',
                'class': 'form-select',
                'placeholder': 'Score Preference'
            }
        )
        self.fields['show_output'].widget.attrs.update(
            {
                'id': 'show-output',
                'class': 'form-select',
                'placeholder': 'Show Output'
            }
        )
        self.fields['subjective'].widget.attrs.update(
            {
                'id': 'subjective',
                'class': 'form-select',
                'placeholder': 'Subjective Grading'
            }
        )
        
class SubmissionForm(forms.ModelForm):
    files = forms.FileField()

    class Meta:
        model = Submission
        fields = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['files'].required = True

        self.fields['files'].widget.attrs.update(
            {
                'id': 'user-submission-files',
                'class': 'form-control',
                'multiple': True
            }
        )

class TeamEnrollForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'name'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['name'].widget.attrs.update(
            {
                'id': 'team-name',
                'class': 'form-control',
                'autofocus': True,
                'placeholder': 'Team Name',
            }
        )
        
    def clean_name(self):
        """Strip HTML tags and validate the team name."""
        name = self.cleaned_data.get('name', '')

        name = strip_tags(name).strip()

        return name

class TeamInviteForm(forms.Form):
    def __init__(self, *args, team_invite_limit, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, team_invite_limit + 1):
            self.fields[f'email_{i}'] = forms.EmailField(
                max_length=254,
                required=False,
                widget=forms.EmailInput(
                    attrs={
                        'id': f'email_{i}',
                        'class': 'form-control',
                        'autocomplete': 'email',
                        'placeholder': 'Email Address'
                    }
                )
            )