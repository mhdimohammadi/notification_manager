from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import ChannelViewSet, EmailConfigurationViewSet



router = DefaultRouter()

router.register('channel', ChannelViewSet, basename="channel")
router.register('email_config', EmailConfigurationViewSet, basename="email_config")

app_name = "channel"
urlpatterns = [
    path('', include(router.urls)),
]
