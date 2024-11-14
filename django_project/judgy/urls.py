from django.urls import path
from .views import (
    home_view,
    login_view,
    logout_view,
    register_view,
    verify_view,
    notifications_view,
    notification_clear_view,
    set_timezone_view,
    competition_create_view,
    competition_code_view,
    team_enroll_view,
    team_join_accept_view,
    team_join_decline_view,
    team_leave_view,
    team_invite_view,
    team_invite_accept_view,
    team_invite_decline_view,
    team_name_view,
    competitions_view,
    submissions
)

app_name = 'judgy'

urlpatterns = [
    path('', home_view, name='home'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('register', register_view, name='register'),
    path('verify', verify_view, name='verify'),
    path('notifications', notifications_view, name='notifications'),
    path('notification/<str:id>/clear', notification_clear_view, name='notification_clear'),
    path('set-timezone', set_timezone_view, name='set_timezone'),
    path('competition/create', competition_create_view, name='competition_create'),
    path('competition/<str:code>', competition_code_view, name='competition_code'),
    path('competition/<str:code>/team/enroll', team_enroll_view, name='team_enroll'),
    path('team/join/<str:id>/accept', team_join_accept_view, name='team_join_accept'),
    path('team/join/<str:id>/decline', team_join_decline_view, name='team_join_decline'),
    path('competition/<str:code>/team/leave', team_leave_view, name='team_leave'),
    path('competition/<str:code>/team/invite', team_invite_view, name='team_invite'),
    path('team/invite/<str:id>/accept', team_invite_accept_view, name='team_invite_accept'),
    path('team/invite/<str:id>/decline', team_invite_decline_view, name='team_invite_decline'),
    path('competition/<str:code>/team/<str:name>', team_name_view, name='team_name'),
    path('competitions', competitions_view, name='competitions'),
    path('submissions', submissions, name='submissions')
]
