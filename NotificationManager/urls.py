from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls', namespace='account')),
    path('', include('channel.urls', namespace='channel')),
    path('', include('notification.urls', namespace='notification')),
    path('', include('notification_log.urls', namespace='notification_log')),
]
