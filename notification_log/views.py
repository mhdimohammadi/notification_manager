from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from notification.models import Notification
from notification_log.serializers import NotificationLogSerializer
from notification_log.services.notif_log import NotificationLogService





class LogView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request, pk=None):
        Notification.objects.get(pk=pk)
        logs = NotificationLogService.get_log_for_notification(pk)
        serializer = NotificationLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
