# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import localtime
from notifications.models import Notification, TeamJoinNotification, TeamInviteNotification
from notifications.utils import send_notification



@receiver(post_save, sender=Notification)
@receiver(post_save, sender=TeamJoinNotification)
@receiver(post_save, sender=TeamInviteNotification)
def push_notification(sender, instance, created, **kwargs):
    if created:
        data = [{
            "id": instance.id,
            "type": instance.type,
            "header": instance.header,
            "body": instance.body,
            "created_at": localtime(instance.created_at).isoformat(),
        }]
        send_notification(instance.user, data)


