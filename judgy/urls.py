from django.urls import path
from .views import (
    home_view,
    login_view,
    logout_view,
    register_view,
    verify_view,
    set_timezone_view,
    competition_create_view,
    competition_code_view,
    search_view,
    submissions
)

app_name = 'judgy'

urlpatterns = [
    path('', home_view, name='home'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('register', register_view, name='register'),
    path('verify', verify_view, name='verify'),
    path('set-timezone', set_timezone_view, name='set_timezone'),
    path('competition/create', competition_create_view, name='competition_create'),
    path('competition/<str:code>', competition_code_view, name='competition_code'),
    path('search', search_view, name='search'),
    path('submissions', submissions, name='submissions')
]
