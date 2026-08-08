from django.urls import path , include
from . import views
from rest_framework import routers

from rest_framework.routers import DefaultRouter

from .views import ChannelViewSet


router = DefaultRouter()

router.register('',ChannelViewSet,basename="channel")




app_name = "channel"
urlpatterns = [
    path('', include(router.urls)),
]
