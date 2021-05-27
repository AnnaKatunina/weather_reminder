from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from weather_app.models import User, Subscription, CityInSubscription
from weather_app.tasks import send_email_task


class MySubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@test.com', password='test_password')
        self.subscription = Subscription.objects.create(user=self.user, period_notifications=3)

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('subscription')

    def test_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_get_subscription(self, mock_has_permission):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'user_email': 'test@test.com', 'period_notifications': 3, 'cities': []})

    @patch('weather_app.views.edit_task')
    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_change_subscription(self, mock_has_permission, mock_edit_task):
        data_subscription = {
            'period_notifications': 6,
        }
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=data_subscription)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'user_email': 'test@test.com', 'period_notifications': 6, 'cities': []})

    @patch('weather_app.views.delete_task')
    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_delete_subscription(self, mock_has_permission, mock_delete_task):
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'Subscription has been deleted')


class MySubscriptionCreateTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email='test@test.com', password='test_password')

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('subscription')

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_create_subscription(self, mock_has_permission):
        data_subscription = {
            'user': self.user.id,
            'period_notifications': 6,
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data_subscription)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class MyCitiesInSubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email='test@test.com', password='test_password')
        self.subscription = Subscription.objects.create(user=self.user, period_notifications=3)
        CityInSubscription.objects.create(subscription=self.subscription, name='London')
        CityInSubscription.objects.create(subscription=self.subscription, name='Berlin')

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('cities')

    def test_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_get_list_cities(self, mock_has_permission):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [{'name': 'London'}, {'name': 'Berlin'}])

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_create_added_city(self, mock_has_permission):
        data_subscription = {
            'subscription': self.subscription,
            'name': 'London',
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data_subscription)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 'City already added in your subscription')

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_create_non_existent_city(self, mock_has_permission):
        data_subscription = {
            'subscription': self.subscription,
            'name': 'aaaaabbbbcccc',
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data_subscription)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, "City doesn't exist")

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_create_city(self, mock_has_permission):
        data_subscription = {
            'subscription': self.subscription,
            'name': 'Kyiv',
        }
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data_subscription)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'name': data_subscription['name']})


class OneCityTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email='test@test.com', password='test_password')
        self.subscription = Subscription.objects.create(user=self.user, period_notifications=3)
        self.city = CityInSubscription.objects.create(subscription=self.subscription, name='Moscow')
        self.url = reverse('one_city', args=[self.city.id])

    def test_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_get_city(self, mock_has_permission):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'name': self.city.name})

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_delete_city(self, mock_has_permission):
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url)
        is_city = CityInSubscription.objects.filter(name=self.city.name)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(is_city)


class GetWeatherTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email='test@test.com', password='test_password')
        self.subscription = Subscription.objects.create(user=self.user, period_notifications=3)
        self.city_1 = CityInSubscription.objects.create(subscription=self.subscription, name='Moscow')
        self.city_2 = CityInSubscription.objects.create(subscription=self.subscription, name='Berlin')

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('get_weather')

    @patch('rest_framework_api_key.permissions.HasAPIKey.has_permission')
    def test_get_weather(self, mock_has_permission):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ViewTestCase(TestCase):

    def test_unauthorized_redirect(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 302)

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')


class TaskTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create(email='test_1@test.com', password='test_password')
        self.user_2 = User.objects.create(email='test_2@test.com', password='test_password')
        self.subscription_1 = Subscription.objects.create(user=self.user_1, period_notifications=3)
        self.subscription_2 = Subscription.objects.create(user=self.user_2, period_notifications=3)
        self.city_1 = CityInSubscription.objects.create(subscription=self.subscription_1, name='Moscow')
        self.city_2 = CityInSubscription.objects.create(subscription=self.subscription_1, name='Berlin')

    @patch('weather_app.tasks.get_weather')
    def test_called_send_mail(self, mock_get_weather):
        sub_id = self.subscription_1.id
        send_email_task(sub_id)
        self.assertEqual(mock_get_weather.call_count, 2)

    @patch('weather_app.tasks.get_weather')
    def test_uncalled_send_mail(self, mock_get_weather):
        sub_id = self.subscription_2.id
        send_email_task(sub_id)
        self.assertEqual(mock_get_weather.call_count, 0)
