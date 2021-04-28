from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from weather_app.views import *

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/subscription/', MySubscriptionView.as_view(), name='subscription'),
    path('api/subscription/cities/', MyCitiesListView.as_view(), name='cities'),
    path('api/subscription/cities/<pk>/', OneCityView.as_view(), name='one_city'),
]
