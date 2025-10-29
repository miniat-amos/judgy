# notifications/utils.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_notification(user, data):
    """Send a notification payload to a user's WebSocket group."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}_notifications",  # group name (matches consumer)
        {
            "type": "notify",  # calls NotificationConsumer.notify
            "data": data,      # sent to client
        }
    )
