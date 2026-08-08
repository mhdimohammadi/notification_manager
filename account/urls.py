from django.urls import path , include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('', views.UserViewSet, basename='account')

app_name = "account"
urlpatterns = [
    path('', include(router.urls)),
]

