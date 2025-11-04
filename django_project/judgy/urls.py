from django.urls import path
from judgy.views.home_view import home_view
from judgy.views.login_view import login_view
from judgy.views.logout_view import logout_view
from judgy.views.register_view import register_view
from judgy.views.verify_view import verify_view
from judgy.views.forgot_password_view import forgot_password_view
from judgy.views.reset_password_view import reset_password_view
from judgy.views.set_timezone_view import set_timezone_view

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

]
