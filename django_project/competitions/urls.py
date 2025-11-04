from django.urls import path

from competitions.views.see_competition_view import see_competitions_view
from competitions.views.competition_create_view import competition_create_view
from competitions.views.problems_update_view import problems_update_view
from competitions.views.competition_code_view import competition_code_view
from competitions.views.competitions_view import competitions_view
from competitions.views.team_enroll_view import team_enroll_view
from competitions.views.team_join_accept_view import team_join_accept_view
from competitions.views.team_join_decline_view import team_join_decline_view
from competitions.views.team_leave_view import team_leave_view
from competitions.views.team_invite_view import team_invite_view
from competitions.views.team_invite_accept_view import team_invite_accept_view
from competitions.views.team_invite_decline_view import team_invite_decline_view
from competitions.views.team_name_view import team_name_view
from competitions.views.download_view import download_view
from competitions.views.submit_view import submit_view
from competitions.views.rankings_view import rankings_view
from competitions.views.output_view import output_view
from competitions.views.get_teams_view import get_teams_view
from competitions.views.get_members_view import get_members_view
from competitions.views.get_member_scores_view import get_member_scores
from competitions.views.admin_comp_interface_view import admin_comp_interface
from competitions.views.admin_team_interface_view import admin_team_interface
from competitions.views.admin_score_input_view import ScoreUpdate


from competitions.views.compUpdate_view import CompUpdate



app_name = 'competitions'

urlpatterns = [
    path('competitions', competitions_view, name='competitions'),
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
    path('competition/<str:code>/<str:problem_name>/download', download_view, name='download'),
    path('competition/<str:code>/<str:problem_name>/submit', submit_view, name='submit'),
    path('competition/<str:code>/rankings', rankings_view, name='rankings'),
    path('competition/<str:code>/<str:problem_name>/submission/output', output_view, name='output'),
    path('competition/<str:code>/teams', get_teams_view, name='competition_teams'),
    path('competition/<str:code>/team/<str:name>/members', get_members_view, name='team_members'),
    path('competition/<str:code>/team/<str:name>/members-scores', get_member_scores, name='members_scores'),
    path('competition/<str:code>/admin-interface', admin_comp_interface, name="admin_comp_interface"),
    path('competition/<str:code>/team/<str:name>/admin-interface', admin_team_interface, name="admin_team_interface"),
    path('competition/<str:code>/update', CompUpdate.as_view(), name="update_competition"),
    path('score/<int:pk>/update', ScoreUpdate.as_view(), name="update_score")

]
