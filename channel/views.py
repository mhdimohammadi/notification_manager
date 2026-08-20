from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Channel, EmailConfiguration
from .serializers import ChannelSerializer, EmailSerializer
from rest_framework.permissions import IsAdminUser,IsAuthenticated


class ChannelViewSet(ModelViewSet):
    serializer_class = ChannelSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Channel.objects.all()

        return Channel.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ["list","retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


    @action(detail=True, methods=['POST'])
    def activate(self, request, pk=None):
        channel = self.get_object()
        channel.is_active = True
        channel.save()
        return Response({"message": f"Channel {channel.name} activated."})

    @action(detail=True, methods=['POST'])
    def deactivate(self, request, pk=None):
        channel = self.get_object()
        channel.is_active = False
        channel.save()
        return Response({"message": f"Channel {channel.name} deactivated."})


class EmailConfigurationViewSet(ModelViewSet):
    queryset = EmailConfiguration.objects.select_related('channel')
    serializer_class = EmailSerializer
    permission_classes = [IsAdminUser]

