from django.urls import path
from .views.home_view import home_view
from .views.see_competition_view import see_competitions_view
from .views.login_view import login_view
from .views.logout_view import logout_view
from .views.register_view import register_view
from .views.verify_view import verify_view
from .views.forgot_password_view import forgot_password_view
from .views.reset_password_view import reset_password_view
from .views.set_timezone_view import set_timezone_view
from .views.competition_create_view import competition_create_view
from .views.competition_code_view import competition_code_view
from .views.problems_update_view import problems_update_view
from .views.team_enroll_view import team_enroll_view
from .views.team_join_accept_view import team_join_accept_view
from .views.team_join_decline_view import team_join_decline_view
from .views.team_leave_view import team_leave_view
from .views.team_invite_view import team_invite_view
from .views.team_invite_accept_view import team_invite_accept_view
from .views.team_invite_decline_view import team_invite_decline_view
from .views.team_name_view import team_name_view
from .views.competitions_view import competitions_view
from .views.download_view import download_view
from .views.submit_view import submit_view
from .views.output_view import output_view
from .views.rankings_view import rankings_view
from .views.get_members_view import get_members_view
from .views.get_teams_view import get_teams_view
from .views.compUpdate_view import CompUpdate
from .views.admin_comp_interface import admin_comp_interface
from .views.admin_team_interface import admin_team_interface
from .views.get_member_scores_view import get_member_scores
from .views.admin_score_input_view import ScoreUpdate

app_name = 'judgy'

urlpatterns = [
    path('', home_view, name='home'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('register', register_view, name='register'),
    path('verify', verify_view, name='verify'),
    path('forgot-password', forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>', reset_password_view, name='reset_password'),
    path('set-timezone', set_timezone_view, name='set_timezone'),
    path('all-competitions', see_competitions_view, name='see_competitions'),
    path('competition/create', competition_create_view, name='competition_create'),
    path('competition/<str:code>/problems/update', problems_update_view, name='problems_update'),
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
    path('competition/<str:code>/<str:problem_name>/download', download_view, name='download'),
    path('competition/<str:code>/<str:problem_name>/submit', submit_view, name='submit'),
    path('competition/<str:code>/rankings', rankings_view, name='rankings'),
    path('competition/<str:code>/<str:problem_name>/submission/output', output_view, name='output'),
    path('competition/<str:code>/team/<str:name>/members', get_members_view, name='team_members'),
    path('competition/<str:code>/teams', get_teams_view, name='competition_teams'),
    path('competition/<str:code>/team/<str:name>/members-scores', get_member_scores, name='members_scores'),
    path('competition/<str:code>/update', CompUpdate.as_view(), name="update_competition"),
    path('competition/<str:code>/admin-interface', admin_comp_interface, name="admin_comp_interface"),
    path('competition/<str:code>/team/<str:name>/admin-interface', admin_team_interface, name="admin_team_interface"),
    path('score/<int:pk>/update', ScoreUpdate.as_view(), name="update_score")

]
