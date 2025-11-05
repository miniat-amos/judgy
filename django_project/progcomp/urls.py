from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('judgy.urls')),
    path('', include('competition.urls')),
    path('', include('notifications.urls')),
    path('admin', admin.site.urls),
]
