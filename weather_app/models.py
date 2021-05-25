import json

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Subscription(models.Model):

    class Period(models.IntegerChoices):
        ONE = 1
        THREE = 3
        SIX = 6
        TWELVE = 12

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    period_notifications = models.IntegerField(choices=Period.choices)
    date_of_subscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} has a subscription since {self.date_of_subscription} ' \
               f'with period of notifications - {self.period_notifications} hours.'


class CityInSubscription(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'


def create_task(subscription):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=subscription.period_notifications,
        period=IntervalSchedule.HOURS
    )
    task = PeriodicTask.objects.create(
        name=f'Send email to {subscription.user.email}',
        task='send_email_task',
        interval=schedule,
        args=json.dumps([subscription.id]),
        start_time=timezone.now()
    )
    task.save()
    return


def edit_task(subscription):
    task = PeriodicTask.objects.filter(name=f'Send email to {subscription.user.email}').first()
    task.interval.every = subscription.period_notifications
    task.interval.save()
    task.save()
    return


def delete_task(subscription):
    task = PeriodicTask.objects.filter(name=f'Send email to {subscription.user.email}').first()
    task.delete()
    return
