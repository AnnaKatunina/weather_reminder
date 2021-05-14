import datetime
import json

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from weather_app.models import Subscription


@receiver(post_save, sender=Subscription)
def create_or_update_periodic_task(sender, instance, created, **kwargs):
    if created:
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=instance.period_notifications,
            period=IntervalSchedule.MINUTES
        )
        instance.task = PeriodicTask.objects.create(
            name=f'Send email to {instance.user.email}',
            task='send_email_task',
            interval=schedule,
            args=json.dumps([instance.id]),
            start_time=timezone.now()
        )
