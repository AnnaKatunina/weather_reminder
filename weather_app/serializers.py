from rest_framework import serializers

from weather_app.models import Subscription, CityInSubscription


class CityInSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CityInSubscription
        fields = ('name', )


class SubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    cities = CityInSubscriptionSerializer(read_only=True, many=True)

    class Meta:
        model = Subscription
        fields = ('user_email', 'period_notifications', 'cities')
