import requests

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView
from decouple import config
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from WeatherReminder.settings import OPEN_WEATHER_API_URL
from weather_app.forms import RegisterForm
from weather_app.models import Subscription, CityInSubscription, create_task, delete_task, edit_task
from weather_app.tasks import get_weather
from weather_app.serializers import SubscriptionSerializer, CityInSubscriptionSerializer


def check_existing_city(city_name):
    url = OPEN_WEATHER_API_URL + f'?q={city_name}&appid={config("weather_api_key")}'
    r = requests.get(url)
    return r.status_code != 200


class MainView(LoginRequiredMixin, View):
    login_url = 'register'

    def get(self, request):
        api_key = config('my_service_api_key')
        context = {
            'api_key': api_key,
        }
        return render(request, 'main.html', context=context)


class RegisterView(CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('main')
    template_name = 'register.html'

    def form_valid(self, form):
        valid = super(RegisterView, self).form_valid(form)
        email, password = form.cleaned_data.get('email'), form.cleaned_data.get('password1')
        new_user = authenticate(email=email, password=password)
        login(self.request, new_user)
        return valid

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super(RegisterView, self).dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('main'))


class MySubscriptionView(APIView):

    def get(self, request):
        subscription = Subscription.objects.filter(user=request.user).first()
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    def post(self, request):
        new_subscription = Subscription.objects.create(
            user=request.user,
            period_notifications=request.data["period_notifications"]
        )
        new_subscription.save()
        create_task(new_subscription)
        serializer = SubscriptionSerializer(new_subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        subscription = Subscription.objects.get(user=request.user.id)
        subscription.period_notifications = request.data["period_notifications"]
        subscription.save()
        edit_task(subscription)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    def delete(self, request):
        subscription = Subscription.objects.get(user=request.user.id)
        delete_task(subscription)
        subscription.delete()
        return Response("Subscription has been deleted")


class MyCitiesListView(ListCreateAPIView):
    serializer_class = CityInSubscriptionSerializer

    def get_queryset(self):
        return CityInSubscription.objects.filter(subscription__user=self.request.user.id)

    def create(self, request, *args, **kwargs):
        input_city = request.data['name']
        existing_city = CityInSubscription.objects.filter(subscription__user=self.request.user.id, name=input_city)
        if existing_city:
            return Response("City already added in your subscription")
        if check_existing_city(input_city):
            return Response("City doesn't exist")
        subscription = Subscription.objects.get(user=request.user.id)
        new_city = CityInSubscription.objects.create(
            subscription=subscription,
            name=input_city,
        )
        new_city.save()
        serializer = CityInSubscriptionSerializer(new_city)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OneCityView(RetrieveDestroyAPIView):
    serializer_class = CityInSubscriptionSerializer

    def get_queryset(self):
        return CityInSubscription.objects.filter(subscription__user=self.request.user.id)


class GetWeatherView(APIView):

    def get(self, request):
        cities = CityInSubscription.objects.filter(subscription__user=request.user.id)
        response_get_weather = []
        for city in cities:
            response_get_weather.append(get_weather(city.name))
        return Response(response_get_weather)
