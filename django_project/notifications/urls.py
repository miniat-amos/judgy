from django.urls import path
from notifications.views.notifications_view import notifications_view
from notifications.views.notification_clear_view import notification_clear_view
from notifications.views.notification_center_view import notification_center_view

app_name = 'notifications'

urlpatterns = [
    path('all_notifications', notifications_view, name='all_notifications'),
    path('notification/<str:id>/clear', notification_clear_view, name='notification_clear'),
    path('notification/center', notification_center_view, name='notification_center')
]
