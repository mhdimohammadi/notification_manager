from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Channel, EmailConfiguration
from .serializers import ChannelSerializer, EmailSerializer


class ChannelViewSet(ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

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
