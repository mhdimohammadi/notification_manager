from django.urls import path
from .views import LogView




app_name = "notification_log"
urlpatterns = [
    path('<int:pk>/logs/',LogView.as_view(),name='logs'),
]