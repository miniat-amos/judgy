# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from judgy.models import Notification
from .utils import send_notification

@receiver(post_save, sender=Notification)
def push_notification(sender, instance, created, **kwargs):
    if created:
        data = [{
            "id": instance.id,
            "type": instance.type,
            "header": instance.header,
            "body": instance.body,
        }]
        send_notification(instance.user, data)
