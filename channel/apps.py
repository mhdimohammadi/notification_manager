from django.apps import AppConfig


class ChannelConfig(AppConfig):
    name = 'channel'


    def ready(self):
        from . import signals