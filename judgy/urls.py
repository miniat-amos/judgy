from django.urls import include, path
from . import views

app_name = 'judgy'

urlpatterns = [
    path('', views.home, name='home')
]
