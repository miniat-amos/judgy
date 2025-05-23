from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Team, Problem, Submission, Competition

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'competition', 'get_members',)

    def get_members(self, obj):
        return ", ".join([user.email for user in obj.members.all()])
    get_members.short_description = 'Members'
    
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('competition', 'number', 'name', 'score_preference')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('problem', 'team', 'user__first_name', 'language', 'file_name', 'score', 'time',)

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'start', 'end', 'enroll_start', 'enroll_end',)