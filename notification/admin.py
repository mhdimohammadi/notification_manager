from django.contrib import admin
from notification.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False





