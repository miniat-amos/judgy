# myproject/websocket_urls.py
from django.urls import re_path
from notifications import consumers as notifications_consumers
from competition import consumers as competitions_consumers

websocket_urlpatterns = [
    re_path(r"ws/notifications/$", notifications_consumers.NotificationConsumer.as_asgi()),
    re_path(r"ws/scores/(?P<competition_code>\w+)/$", competitions_consumers.ScoreConsumer.as_asgi()),

]