from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChannelViewSet, EmailConfigurationViewSet



router = DefaultRouter()

router.register(r'channel', ChannelViewSet, basename="channel")
router.register(r'email_config', EmailConfigurationViewSet, basename="email_config")

app_name = "channel"
urlpatterns = [
    path('', include(router.urls)),
]
