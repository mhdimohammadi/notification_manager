from rest_framework import status, viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from .tasks import dispatch_notification
from .services.idempotency import NotificationIdempotency
from django.db import transaction
from notification.services.notification_ratelimit import NotificationRateLimit




class NotificationViewSet(CreateModelMixin,ListModelMixin,RetrieveModelMixin,viewsets.GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_create(self, serializer):
        idempotency_key = self.request.headers["Idempotency-Key"]

        with transaction.atomic():
            notification = serializer.save()
            self._created_notification = notification

            def after_commit():
                NotificationIdempotency.set_result(idempotency_key,notification.id)
                dispatch_notification.delay(notification_id=notification.id)

            transaction.on_commit(after_commit)

    def create(self, request, *args, **kwargs):
        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response({"detail": "Idempotency-Key header is required."},status=status.HTTP_400_BAD_REQUEST)


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        claimed = NotificationIdempotency.claim(idempotency_key)

        if not claimed:
            existing_id = NotificationIdempotency.get(idempotency_key)

            if existing_id == NotificationIdempotency.PROCESSING:
                return Response({"detail": "This request is already being processed."},status=status.HTTP_409_CONFLICT)


            notification = Notification.objects.get(pk=existing_id)
            return Response(self.get_serializer(notification).data,status=status.HTTP_202_ACCEPTED)


        identifier = request.META.get("REMOTE_ADDR")


        if not identifier:
            NotificationIdempotency.delete(idempotency_key)
            return Response({"detail": "Unable to determine client identity."},status=status.HTTP_400_BAD_REQUEST)

        if not NotificationRateLimit.check(identifier):
            NotificationIdempotency.delete(idempotency_key)
            return Response({"detail": "too many requests. Try again later."},status=status.HTTP_429_TOO_MANY_REQUESTS)


        try:
            self.perform_create(serializer)
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)

        except Exception:
            NotificationIdempotency.delete(idempotency_key)
            raise