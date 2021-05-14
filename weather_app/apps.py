from django.apps import AppConfig


class WeatherAppConfig(AppConfig):
    name = 'weather_app'

    def ready(self):
        from weather_app import signals
