from django.urls import path, include
from . import views

app_name = "judgy"

urlpatterns = [
    path("", views.home, name="Homepage")
    ]