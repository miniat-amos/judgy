from django.urls import path
from .views.notifications_view import notifications_view
from .views.notification_clear_view import notification_clear_view

app_name = 'notifications'

urlpatterns = [
    path('notifications', notifications_view, name='notifications'),
    path('notification/<str:id>/clear', notification_clear_view, name='notification_clear'),
]
