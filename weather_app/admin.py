from django.contrib import admin

from weather_app.models import User, Subscription, CityInSubscription

admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(CityInSubscription)
